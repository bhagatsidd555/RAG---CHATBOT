"""
embedder.py
Free, local embeddings using sentence-transformers.
Model: all-MiniLM-L6-v2  (~80 MB, no API key, runs on CPU)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import EMBED_MODEL

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"[Embedder] Loading '{EMBED_MODEL}' (first load may take ~30s)...")
        _model = SentenceTransformer(EMBED_MODEL)
        print("[Embedder] Model loaded ✓")
    return _model


def embed_texts(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    """Embed a list of texts. Returns list of float vectors."""
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=len(texts) > 50,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


from functools import lru_cache

@lru_cache(maxsize=500)
def embed_query(query: str):

    model = get_model()

    vec = model.encode(
        [query],
        normalize_embeddings=True
    )

    return vec[0].tolist()