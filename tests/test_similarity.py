import numpy as np
import pytest

from src.inference.similarity import cosine_matrix, max_pairwise, select_diverse


def test_cosine_and_max_pairwise():
    sim = cosine_matrix([[1, 0], [0, 1], [1, 1]])
    assert sim[0, 1] == pytest.approx(0)
    assert max_pairwise(sim) == pytest.approx(2 ** -0.5)
    assert max_pairwise(np.array([[1.0]])) == 0.0


def test_select_diverse_avoids_near_duplicates():
    rng = np.random.default_rng(0)
    base = np.eye(5)                                   # five orthogonal directions
    dupes = base[0] + rng.normal(0, 0.01, (20, 5))     # twenty near copies of the first
    emb = np.vstack([base, dupes])
    idx, sim = select_diverse(emb, k=5, max_sim=0.5, seed=1)
    assert len(set(idx)) == 5
    assert max_pairwise(sim) < 0.5


def test_select_diverse_fails_when_pool_is_too_similar():
    emb = np.array([[1, 0.01 * i] for i in range(10)], dtype=float)
    with pytest.raises(ValueError):
        select_diverse(emb, k=5, max_sim=0.8)


def test_select_diverse_needs_enough_candidates():
    with pytest.raises(ValueError):
        select_diverse(np.eye(3), k=5, max_sim=0.8)
