"""Path standardisation with shortlists (scripts/1_path_standardisation/1.02_rnv_run_path_standardisation.py).

For every path, find the path of the catalogue (the largest donation) that holds the same data, or NA. In steps, each
cheaper than the next:

1. exact:   the path is in the catalogue.
2. clean:   after removing wrapper folders and part numbers (src/ingest/cleanPaths.py, ingest step 0.06) the path is the
            same as a catalogue path.
3. file:    the paths that are left are grouped by file. For every file the model chooses among a shortlist of the
            catalogue files whose names are most similar (multilingual embeddings), or says that none is the same file.
            Paths of a file without a match are NA.
4. field:   in a matched file a field is matched to the fields of the catalogue file, directly if the name is the same,
            otherwise by the model, again from a shortlist.

The model only ever sees a numbered shortlist and answers with a number, so it cannot return a path that is not in the
catalogue. `ask` (prompt -> text) and `embedder` (list of texts -> unit-length vectors) are passed in, so everything here
can be tested without a model.
"""

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from src.ingest.cleanPaths import clean_path, match_key, split_unit
from src.inference.pathmatch import NA
from src.inference.retrieval import embed_text, top_k
from src.inference.taxonomy import extract_json_dict

MAX_FIELDS_SHOWN = 6   # field names shown next to a file in the file prompt


def numbered(lines):
    return "\n".join(f"{i}. {line}" for i, line in enumerate(lines, 1))


def build_choice_prompt(template, candidates, query):
    """Fill {CANDIDATES} (numbered) and {QUERY}. Plain replace: the prompt contains JSON braces. {QUERY} is last."""
    return template.replace("{CANDIDATES}", numbered(candidates)).replace("{QUERY}", query)


def parse_choice(raw, n_candidates):
    """The model's JSON object if "choice" is an integer from 0 (none) to n_candidates and there is a rationale, else None."""
    obj = extract_json_dict(raw)
    if not obj:
        return None
    choice = obj.get("choice")
    if isinstance(choice, bool) or not isinstance(choice, int) or not 0 <= choice <= n_candidates:
        return None
    if not isinstance(obj.get("rationale"), str) or not obj["rationale"].strip():
        return None
    return obj


def leaf(field):
    return field.rsplit("/", 1)[-1] if field else ""


def fields_hint(fields):
    names = []
    for f in fields:
        name = leaf(f)
        if name and name not in names:
            names.append(name)
    shown = ", ".join(names[:MAX_FIELDS_SHOWN]) + (", ..." if len(names) > MAX_FIELDS_SHOWN else "")
    return f"  [fields: {shown}]" if names else ""


class Catalogue:
    """The catalogue, indexed by path, by file and by field. Keys are match_key(clean path), so wrapper folders, part
    numbers, case and separators do not matter. Paths of one catalogue that only differ in such ways keep the first one."""

    def __init__(self, raw_paths, clean_paths):
        self.raw_set = set(raw_paths)
        self.by_key = {}      # match_key(clean path) -> catalogue path
        self.units = {}       # match_key(file) -> {"unit": file, "fields": {match_key(field): (field, catalogue path)}}
        for raw, clean in zip(raw_paths, clean_paths):
            key = match_key(clean)
            if key in self.by_key:
                continue
            self.by_key[key] = raw
            unit, field = split_unit(clean)
            entry = self.units.setdefault(match_key(unit), {"unit": unit, "fields": {}})
            entry["fields"].setdefault(match_key(field), (field, raw))
        self.unit_keys = list(self.units)


class ShortlistMatcher:
    def __init__(self, catalogue, embedder, ask, file_template, field_template, k=15, workers=100, retries=3):
        self.cat, self.embedder, self.ask = catalogue, embedder, ask
        self.file_template, self.field_template = file_template, field_template
        self.k, self.workers, self.retries = k, workers, retries
        self._unit_emb = None
        self._field_emb = {}

    # -- model -------------------------------------------------------------------------------------------------

    def _choose(self, template, candidates, query):
        """(choice, rationale) from the model, or None if no valid answer after the retries."""
        prompt = build_choice_prompt(template, candidates, query)
        for _ in range(self.retries):
            obj = parse_choice(self.ask(prompt), len(candidates))
            if obj is not None:
                return obj["choice"], obj["rationale"].strip()
        return None

    def _map(self, jobs):
        """Run the (still lazy) model calls in parallel; results in the order of the jobs."""
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            return list(pool.map(lambda job: job(), jobs))

    # -- shortlists --------------------------------------------------------------------------------------------

    def unit_embeddings(self):
        if self._unit_emb is None:
            self._unit_emb = self.embedder([embed_text(self.cat.units[k]["unit"]) for k in self.cat.unit_keys])
        return self._unit_emb

    def field_list(self, unit_key):
        """Fields of a catalogue file (the file itself, field "", is not a field)."""
        return [f for f, _ in self.cat.units[unit_key]["fields"].values() if f]

    def field_embeddings(self, unit_key):
        if unit_key not in self._field_emb:
            self._field_emb[unit_key] = self.embedder([embed_text(f, last=3) for f in self.field_list(unit_key)])
        return self._field_emb[unit_key]

    # -- the steps ---------------------------------------------------------------------------------------------

    def match(self, paths, clean_of=None):
        """-> (records in the order of `paths`, failed). A record is
        {"path", "match" (catalogue path or NA), "rationale", "method", "file_match"}; method is exact, clean, llm or
        file_na. `failed` lists paths for which the model gave no valid answer. `clean_of` maps a path to its clean path
        (from the ingest step); paths missing from it are cleaned here."""
        clean_of = clean_of or {}
        records, failed, groups = {}, [], defaultdict(list)

        for path in paths:
            if path in self.cat.raw_set:
                records[path] = _rec(path, path, "The path is in the catalogue.", "exact", path)
                continue
            clean = clean_of.get(path) or clean_path(path)
            raw = self.cat.by_key.get(match_key(clean))
            if raw is not None:
                records[path] = _rec(path, raw, "The path is the same as this catalogue path after removing wrapper "
                                                "folders and part numbers.", "clean", raw)
                continue
            unit, field = split_unit(clean)
            groups[match_key(unit)].append((path, unit, field))

        file_choice = self._match_files(groups)            # unit key -> (catalogue unit key | None, rationale) | None
        needs_model = defaultdict(list)                    # catalogue unit key -> [(path, unit, field, file rationale)]
        for ukey, items in groups.items():
            decision = file_choice[ukey]
            if decision is None:
                failed += [{"path": p, "error": "invalid output (file match)"} for p, _, _ in items]
                continue
            cat_key, why = decision
            if cat_key is None:
                for p, _, _ in items:
                    records[p] = _rec(p, NA, why, "file_na", NA)
                continue
            entry = self.cat.units[cat_key]
            for p, unit, field in items:
                known = self._field_without_model(p, field, entry, why)
                if known is not None:
                    records[p] = known
                else:
                    needs_model[cat_key].append((p, unit, field, why))

        jobs, job_paths = [], []
        for cat_key, items in needs_model.items():
            for (p, unit, field, why), candidates in zip(items, self._field_candidates(cat_key, [i[2] for i in items])):
                jobs.append(self._field_job(p, unit, field, cat_key, candidates))
                job_paths.append(p)
        for p, rec in zip(job_paths, self._map(jobs)):
            if rec is None:
                failed.append({"path": p, "error": "invalid output (field match)"})
            else:
                records[p] = rec

        return [records[p] for p in paths if p in records], failed

    def _match_files(self, groups):
        """Decide, for each file of the input (unit key), which catalogue file it is, or none."""
        decisions, jobs, job_keys = {}, [], []
        todo = []
        for ukey, items in groups.items():
            if ukey in self.cat.units:
                decisions[ukey] = (ukey, "The file is the same after removing wrapper folders and part numbers.")
            else:
                todo.append(ukey)
        if todo and self.cat.unit_keys:
            texts = [embed_text(groups[u][0][1]) for u in todo]
            shortlists = top_k(self.embedder(texts), self.unit_embeddings(), self.k)
            for ukey, shortlist in zip(todo, shortlists):
                cand_keys = [self.cat.unit_keys[i] for i in shortlist]
                candidates = [self.cat.units[c]["unit"] + fields_hint(f for f, _ in self.cat.units[c]["fields"].values())
                              for c in cand_keys]
                unit = groups[ukey][0][1]
                query = unit + fields_hint(field for _, _, field in groups[ukey])
                jobs.append(self._file_job(candidates, cand_keys, query))
                job_keys.append(ukey)
        else:
            for ukey in todo:
                decisions[ukey] = (None, "The catalogue has no files.")
        for ukey, result in zip(job_keys, self._map(jobs)):
            decisions[ukey] = result
        return decisions

    def _file_job(self, candidates, cand_keys, query):
        def run():
            answer = self._choose(self.file_template, candidates, query)
            if answer is None:
                return None
            choice, why = answer
            return (cand_keys[choice - 1] if choice else None), why
        return run

    def _field_without_model(self, path, field, entry, file_why):
        """A finished record when the field needs no model (same name, or nothing to choose from), else None."""
        fkey = match_key(field)
        if fkey in entry["fields"]:
            return _rec(path, entry["fields"][fkey][1], f"{file_why} The field is also the same.", "llm", entry["unit"])
        if not field:
            return _rec(path, NA, f"The file matches {entry['unit']}, but the catalogue has no path for the file itself.",
                        "llm", entry["unit"])
        if not [f for f, _ in entry["fields"].values() if f]:
            return _rec(path, NA, f"The file matches {entry['unit']}, but the catalogue has no fields for it.",
                        "llm", entry["unit"])
        return None

    def _field_candidates(self, cat_key, fields):
        """For each field (of one file): the candidate fields of the catalogue file, at most k, the most similar first."""
        candidates = self.field_list(cat_key)
        if len(candidates) <= self.k:
            return [candidates] * len(fields)
        shortlists = top_k(self.embedder([embed_text(f, last=3) for f in fields]), self.field_embeddings(cat_key), self.k)
        return [[candidates[i] for i in sl] for sl in shortlists]

    def _field_job(self, path, unit, field, cat_key, candidates):
        entry = self.cat.units[cat_key]

        def run():
            query = f"File: {unit}\nCatalogue file: {entry['unit']}\nField: {field}"
            answer = self._choose(self.field_template, candidates, query)
            if answer is None:
                return None
            choice, why = answer
            if choice == 0:
                return _rec(path, NA, why, "llm", entry["unit"])
            raw = entry["fields"][match_key(candidates[choice - 1])][1]
            return _rec(path, raw, why, "llm", entry["unit"])
        return run


def _rec(path, match, rationale, method, file_match):
    return {"path": path, "match": match, "rationale": rationale, "method": method, "file_match": file_match}
