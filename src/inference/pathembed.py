"""Path standardisation with an embedding shortlist of whole paths (scripts/1_path_standardisation/1.02_rnv_run_path_standardisation.py,
PATH_STD=path_embed2026).

Like src/inference/pathshortlist.py, but without the split between file and field: the catalogue is reduced with
multilingual embeddings to the SHORTLIST_K catalogue paths most similar to the path, and the model chooses among those
whole paths (prompt `path_embed2026`) or says that none is the same data.

1. exact: the path is in the catalogue.
2. clean: after removing wrapper folders and part numbers the path is the same as a catalogue path.
3. embed: the model chooses from a numbered shortlist of catalogue paths. NA if none.

The shortlist is built from the last EMBED_SEGMENTS parts of the path (the file and the field), so a field that exists in
many files ("title") is still placed near its own file. The model answers with a number, so it cannot return a path that
is not in the catalogue. Everything else (the model call, retries, the catalogue) is shared with ShortlistMatcher.
"""

from src.ingest.cleanPaths import split_unit
from src.inference.pathmatch import NA
from src.inference.pathshortlist import ShortlistMatcher, _rec
from src.inference.retrieval import embed_text, top_k

EMBED_SEGMENTS = 4   # last parts of a path that are embedded


class EmbedMatcher(ShortlistMatcher):
    def __init__(self, catalogue, embedder, ask, template, k=15, workers=100, retries=3):
        super().__init__(catalogue, embedder, ask, template, None, k=k, workers=workers, retries=retries)
        self._path_emb = None

    def path_embeddings(self):
        if self._path_emb is None:
            self._path_emb = self.embedder([embed_text(c, last=EMBED_SEGMENTS) for _, c in self.cat.entries])
        return self._path_emb

    def match(self, paths, clean_of=None):
        """-> (records in the order of `paths`, failed). A record is {"path", "match" (catalogue path or NA),
        "rationale", "method", "file_match", "shortlist"}; method is exact, clean or llm ("shortlist": the candidates
        shown to the model, development). `failed` lists paths for which the model gave no valid answer."""
        clean_of = clean_of or {}
        records, todo = {}, []
        for path in paths:
            rec, clean = self._without_model(path, clean_of)
            if rec is not None:
                records[path] = rec
            else:
                todo.append((path, clean))

        entries = self.cat.entries
        if todo and entries:
            shortlists = top_k(self.embedder([embed_text(c, last=EMBED_SEGMENTS) for _, c in todo]),
                               self.path_embeddings(), self.k)
        else:
            shortlists = [[] for _ in todo]
        jobs = [self._job(path, clean, [entries[i] for i in sl]) for (path, clean), sl in zip(todo, shortlists)]

        failed = []
        for (path, _), rec in zip(todo, self._map(jobs)):
            if rec is None:
                failed.append({"path": path, "error": "invalid output (path match)"})
            else:
                records[path] = rec
        return [records[p] for p in paths if p in records], failed

    def _job(self, path, clean, shortlist):
        candidates = [c for _, c in shortlist]

        def run():
            if not candidates:
                return _rec(path, NA, "The catalogue has no paths.", "llm", NA)
            answer = self._choose(self.file_template, candidates, clean)
            if answer is None:
                return None
            choice, why = answer
            rec = (_rec(path, NA, why, "llm", NA) if choice == 0 else
                   _rec(path, shortlist[choice - 1][0], why, "llm", split_unit(candidates[choice - 1])[0]))
            rec["shortlist"] = candidates
            return rec
        return run
