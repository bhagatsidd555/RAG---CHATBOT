"""
chroma_db.py
Persist and query embeddings using ChromaDB (free, local, no server needed).
Uses HNSW index internally for fast ANN search.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import CHROMA_DIR, COLLECTION_NAME, TOP_K

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(chunks: List[Dict], embeddings: List[List[float]]):
    """Add chunks + embeddings to ChromaDB in batches."""
    col = get_collection()

    ids        = [c["id"]   for c in chunks]
    documents  = [c["text"] for c in chunks]
    metadatas  = [
        {
            "filename":    c["filename"],
            "page_num":    c["page_num"],
            "chunk_index": c["chunk_index"],
            "source_type": c["source_type"],
        }
        for c in chunks
    ]

    # ChromaDB batch limit = 5461
    BATCH = 500
    for i in range(0, len(ids), BATCH):
        col.add(
            ids=ids[i:i+BATCH],
            embeddings=embeddings[i:i+BATCH],
            documents=documents[i:i+BATCH],
            metadatas=metadatas[i:i+BATCH],
        )
    print(f"[ChromaDB] Stored {len(ids)} chunks ✓")


def query(query_embedding: List[float], top_k: int = TOP_K) -> List[Dict]:
    """
    Query ChromaDB with a query embedding.
    Returns list of result dicts with text, metadata, score.
    """
    col = get_collection()
    count = col.count()
    if count == 0:
        return []

    results = col.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for i in range(len(results["ids"][0])):
        dist = results["distances"][0][i]
        score = 1 - dist   # cosine similarity (higher = better)
        hits.append({
            "id":       results["ids"][0][i],
            "text":     results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score":    round(score, 4),
        })
    return hits


def get_all_documents() -> List[str]:
    """Return list of unique filenames in the collection."""
    col = get_collection()
    if col.count() == 0:
        return []
    results = col.get(include=["metadatas"])
    filenames = list({m["filename"] for m in results["metadatas"]})
    return sorted(filenames)


def collection_count() -> int:
    return get_collection().count()


def delete_collection():
    """Wipe the collection (re-ingest)."""
    global _collection
    col = get_collection()
    _client.delete_collection(COLLECTION_NAME)
    _collection = None
    print("[ChromaDB] Collection deleted.")
