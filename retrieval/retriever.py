"""
retriever.py

Two-stage retrieval:
1. ChromaDB ANN search
2. BM25 reranking
3. Score filtering
4. Fallback if no results survive
"""

import sys
import os
import time

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

from config import TOP_K, RERANK_TOP_K
from embeddings.embedder import embed_query
from vectordb.chroma_db import query as chroma_query

from rank_bm25 import BM25Okapi


# Lower threshold to avoid over-filtering
MIN_SCORE = 0.25


def bm25_rerank(
        query_text,
        hits,
        top_k=RERANK_TOP_K
):

    if not hits:
        return []

    try:

        tokenized_corpus = [

            h["text"]
            .lower()
            .split()

            for h in hits

        ]

        bm25 = BM25Okapi(
            tokenized_corpus
        )

        query_tokens = (
            query_text
            .lower()
            .split()
        )

        bm25_scores = bm25.get_scores(
            query_tokens
        )

        max_bm25 = max(
            bm25_scores
        )

        if max_bm25 <= 0:
            max_bm25 = 1

        # combine vector + lexical scores

        for i, hit in enumerate(hits):

            vector_score = hit.get(
                "score",
                0
            )

            lexical_score = (
                bm25_scores[i]
                / max_bm25
            )

            combined = (
                0.7 * vector_score
                +
                0.3 * lexical_score
            )

            hit[
                "bm25_score"
            ] = round(
                float(
                    bm25_scores[i]
                ),
                4
            )

            hit[
                "combined_score"
            ] = round(
                combined,
                4
            )

        reranked = sorted(

            hits,

            key=lambda x:
            x["combined_score"],

            reverse=True

        )

        # filter low scores

        filtered = []

        for h in reranked:

            score = h[
                "combined_score"
            ]

            if score >= MIN_SCORE:

                filtered.append(
                    h
                )

        # fallback:
        # if everything filtered out
        # keep best 3 results

        if len(filtered) == 0:

            filtered = reranked[:3]

        return filtered[:top_k]

    except Exception as e:

        print(
            f"BM25 error: {e}"
        )

        return hits[:top_k]


def retrieve(
        query_text,
        top_k=TOP_K,
        rerank_top_k=RERANK_TOP_K
):

    t0 = time.time()

    try:

        # Query embedding

        qvec = embed_query(
            query_text
        )

        # Chroma ANN

        candidates = chroma_query(
            qvec,
            top_k=top_k
        )

        # BM25 reranking

        final_hits = bm25_rerank(

            query_text,

            candidates,

            top_k=rerank_top_k

        )

        latency_ms = int(

            (
                time.time()
                -
                t0
            )
            * 1000

        )

        return {

            "query":
            query_text,

            "hits":
            final_hits,

            "candidates":
            len(candidates),

            "returned":
            len(final_hits),

            "latency_ms":
            latency_ms
        }

    except Exception as e:

        print(
            f"Retrieval error:{e}"
        )

        return {

            "query":
            query_text,

            "hits": [],

            "candidates": 0,

            "returned": 0,

            "latency_ms": 0
        }