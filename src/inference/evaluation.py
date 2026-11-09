"""Compare taxonomy output with human annotations (scripts/2_taxonomy/2.06)."""

from collections import Counter


def canonical_label(value, labels):
    """Match a human label to the taxonomy ignoring case, surrounding whitespace and quotes; None if no match."""
    if not isinstance(value, str):
        return None
    key = value.strip().strip('"\'').strip().lower()
    for label in labels:
        if label.lower() == key:
            return label
    return None


def evaluate(records, gold, labels):
    """Accuracy and confusion of the taxonomy model against human labels.

    records: taxonomy records ({"path", "predictions": [{"label", "confidence"}, ...] or None}).
    gold:    {path: human label as written by the annotator}.
    Paths without a valid prediction count as wrong; paths whose human label is not in the taxonomy,
    or that have no human label, are excluded and counted separately.
    """
    labels = sorted(labels)
    by_path = {r["path"]: r for r in records}
    n = top1 = top3 = no_pred = 0
    confusion = Counter()
    per_class = {lab: {"support": 0, "tp": 0, "predicted": 0} for lab in labels}
    unknown_gold = []

    for path, raw in gold.items():
        rec = by_path.get(path)
        if rec is None:
            continue
        truth = canonical_label(raw, labels)
        if truth is None:
            unknown_gold.append({"path": path, "label": raw})
            continue
        preds = [x["label"] for x in (rec.get("predictions") or [])]
        first = preds[0] if preds else None
        n += 1
        no_pred += first is None
        top1 += first == truth
        top3 += truth in preds[:3]
        confusion[(truth, first)] += 1
        per_class[truth]["support"] += 1
        per_class[truth]["tp"] += first == truth
        if first in per_class:
            per_class[first]["predicted"] += 1

    for stats in per_class.values():
        stats["precision"] = stats["tp"] / stats["predicted"] if stats["predicted"] else None
        stats["recall"] = stats["tp"] / stats["support"] if stats["support"] else None

    return {
        "n": n,
        "top1_accuracy": top1 / n if n else None,
        "top3_accuracy": top3 / n if n else None,
        "n_without_prediction": no_pred,
        "n_unannotated": len(set(by_path) - set(gold)),
        "unknown_gold_labels": unknown_gold,
        "per_class": per_class,
        "confusion": [{"truth": t, "predicted": p, "count": c} for (t, p), c in sorted(confusion.items(), key=str)],
    }
