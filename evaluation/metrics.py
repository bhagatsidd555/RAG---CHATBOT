"""
metrics.py

Track:
- Query count
- p50/p95/p99 latency
- Average latency
- Retrieval score
- Ollama availability
"""

import statistics
from collections import deque


LATENCIES = deque(
    maxlen=1000
)

SCORES = deque(
    maxlen=1000
)

QUERY_COUNT = 0

OLLAMA_SUCCESS = 0


def record(
    latency_ms,
    retrieval_score,
    ollama_ok
):

    global QUERY_COUNT
    global OLLAMA_SUCCESS

    QUERY_COUNT += 1

    LATENCIES.append(
        latency_ms
    )

    SCORES.append(
        retrieval_score
    )

    if ollama_ok:
        OLLAMA_SUCCESS += 1


def percentile(
    values,
    p
):

    if not values:
        return 0

    values = sorted(values)

    index = int(
        len(values) * p / 100
    )

    index = min(
        index,
        len(values)-1
    )

    return values[index]


def get_stats():

    lats = list(
        LATENCIES
    )

    scores = list(
        SCORES
    )

    availability = round(

        OLLAMA_SUCCESS /

        max(
            QUERY_COUNT,
            1
        )

        *100,

        2
    )


    avg_latency = (

        round(

            statistics.mean(
                lats
            ),

            2

        )

        if lats else 0
    )


    avg_score = (

        round(

            statistics.mean(
                scores
            ),

            4

        )

        if scores else 0
    )


    min_score = (

        round(
            min(scores),
            4
        )

        if scores else 0
    )


    max_score = (

        round(
            max(scores),
            4
        )

        if scores else 0
    )


    return {

        # frontend stats
        "queries":
        QUERY_COUNT,

        "p50_ms":
        percentile(
            lats,
            50
        ),

        "p95_ms":
        percentile(
            lats,
            95
        ),

        "p99_ms":
        percentile(
            lats,
            99
        ),

        "avg_latency_ms":
        avg_latency,

        "avg_score":
        avg_score,

        "ollama_availability":
        availability,

        "min_score":
        min_score,

        "max_score":
        max_score
    }