"""Semantic-similarity helpers for picking a small, diverse set of paths.

numpy only; the embeddings themselves come from scripts/2_classification/2.00_rnv_select_smoke_sample.py.
"""

import numpy as np


def cosine_matrix(emb) -> np.ndarray:
    """Pairwise cosine similarity of the rows of emb."""
    emb = np.asarray(emb, dtype=float)
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    emb = emb / np.where(norms == 0, 1.0, norms)
    return emb @ emb.T


def max_pairwise(sim) -> float:
    """Largest similarity between two different rows."""
    sim = np.asarray(sim, dtype=float)
    if sim.shape[0] < 2:
        return 0.0
    off_diag = sim[~np.eye(sim.shape[0], dtype=bool)]
    return float(off_diag.max())


def select_diverse(emb, k: int, max_sim: float, seed: int = 42):
    """Pick k rows that are mutually dissimilar (farthest-point selection).

    Starts from a random row, then repeatedly adds the row whose highest similarity to the
    already chosen rows is lowest. Raises ValueError if the chosen rows still contain a pair
    with cosine similarity >= max_sim, i.e. the pool has no diverse enough subset of size k.
    Returns (indices, similarity matrix of the chosen rows).
    """
    emb = np.asarray(emb, dtype=float)
    n = emb.shape[0]
    if n < k:
        raise ValueError(f"Need at least {k} candidates, got {n}")

    sim = cosine_matrix(emb)
    rng = np.random.default_rng(seed)
    chosen = [int(rng.integers(n))]
    closest = sim[chosen[0]].copy()          # highest similarity of every row to the chosen set
    closest[chosen[0]] = np.inf              # never pick a row twice
    while len(chosen) < k:
        nxt = int(np.argmin(closest))
        chosen.append(nxt)
        closest = np.maximum(closest, sim[nxt])
        closest[chosen] = np.inf

    chosen_sim = sim[np.ix_(chosen, chosen)]
    worst = max_pairwise(chosen_sim)
    if worst >= max_sim:
        raise ValueError(
            f"Most dissimilar {k} candidates still have max pairwise cosine {worst:.3f} >= {max_sim}; "
            "raise the pool size or the threshold"
        )
    return chosen, chosen_sim
