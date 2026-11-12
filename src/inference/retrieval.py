"""Embedding-based shortlists for the path standardisation (src/inference/pathshortlist.py).

`Embedder` wraps a sentence-transformers model and runs on the CPU, so it does not compete with the vLLM servers
for GPU memory. `top_k` is plain numpy, so the logic that uses it can be tested with a fake embedder.
"""

import re

import numpy as np


class Embedder:
    """Multilingual sentence embeddings (config.PATH_EMBEDDING_MODEL), loaded on first use. Rows are unit length."""

    def __init__(self, model_path, batch_size=128):
        self.model_path, self.batch_size, self._model = model_path, batch_size, None

    def __call__(self, texts):
        if self._model is None:
            from sentence_transformers import SentenceTransformer   # heavy import, only when needed
            self._model = SentenceTransformer(self.model_path, device="cpu")
        if not texts:
            return np.zeros((0, 1))
        return np.asarray(self._model.encode(list(texts), batch_size=self.batch_size, normalize_embeddings=True,
                                             show_progress_bar=False))


def top_k(query_emb, corpus_emb, k):
    """For each query row: the indices of the k most similar corpus rows (cosine), best first."""
    if len(corpus_emb) == 0:
        return [[] for _ in range(len(query_emb))]
    sims = np.asarray(query_emb) @ np.asarray(corpus_emb).T
    k = min(k, sims.shape[1])
    order = np.argsort(-sims, axis=1)[:, :k]
    return order.tolist()


def embed_text(path_part, last=2):
    """Text to embed for a file or field path: its last segments, with separators as spaces and the extension left out,
    e.g. 'Takeout/YouTube/historial/historial-de-búsquedas.json' -> 'historial / historial de búsquedas'."""
    segs = [s for s in path_part.split("/") if s][-last:]
    segs = [re.sub(r"\.(?:json|js|csv|txt|html|xml)$", "", s, flags=re.IGNORECASE) for s in segs]
    return " / ".join(re.sub(r"[_\-\s]+", " ", s).strip() for s in segs)
