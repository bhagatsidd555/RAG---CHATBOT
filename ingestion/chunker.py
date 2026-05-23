"""
chunker.py
Split page text into overlapping chunks with metadata.
Strategy: word-based sliding window (chunk_size words, overlap words).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import CHUNK_SIZE, CHUNK_OVERLAP
from typing import List, Dict


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 30:   # skip tiny fragments
            chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks


def create_chunks(pages: List[Dict]) -> List[Dict]:
    """
    Given extracted pages, produce chunk dicts with full metadata.
    Each chunk:
      { id, text, filename, page_num, chunk_index, source_type }
    """
    all_chunks = []
    for page in pages:
        text = page["text"]
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{page['filename']}__p{page['page_num']}__c{i}"
            all_chunks.append({
                "id":          chunk_id,
                "text":        chunk,
                "filename":    page["filename"],
                "page_num":    page["page_num"],
                "chunk_index": i,
                "source_type": page["source_type"],
            })

    return all_chunks
