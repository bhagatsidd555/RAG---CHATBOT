"""
generator.py

Generate answers using Ollama
Supports:
llama3
phi3
mistral
gemma

Falls back to extractive mode
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

from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL
)

import httpx
from typing import List,Dict,Tuple


RAG_SYSTEM_PROMPT="""
You are a document question-answer assistant.

STRICT RULES:

1. Answer ONLY from provided context
2. Never use outside knowledge
3. Ignore corrupted text
4. Ignore unreadable symbols
5. If information missing say:

"Not found in uploaded documents"

6. Keep answers below 100 words
7. Always cite:

[filename,page X]

8. Combine multiple contexts if needed

9. Never hallucinate
"""


def build_prompt(
query:str,
hits:List[Dict]
):

    context=[]

    for i,hit in enumerate(
        hits,
        1
    ):

        meta=hit["metadata"]

        context.append(

f"""
[Context {i}]

Source:
{meta['filename']}

Page:
{meta['page_num']}

Content:
{hit['text']}
"""

        )

    context_text="\n---\n".join(
        context
    )

    prompt=f"""

Context:

{context_text}

Question:

{query}

Answer:

"""

    return prompt



def call_ollama(
prompt:str,
model:str=OLLAMA_MODEL
)->Tuple[str,bool]:


    url=f"{OLLAMA_HOST}/api/generate"

    payload={

        "model":
        model,

        "prompt":
        prompt,

        "system":
        RAG_SYSTEM_PROMPT,

        "stream":
        False,

        "options":{

            "temperature":
            0.1,

            "num_predict":
            50,

            "top_k":
            10,

            "top_p":
            0.8
            
        }

    }

    try:

        with httpx.Client(
            timeout=20
        ) as client:

            response=client.post(
                url,
                json=payload
            )

            response.raise_for_status()

            data=response.json()

            return data.get(
                "response",
                ""
            ),True


    except httpx.ConnectError:

        return None,False


    except Exception as e:

        return f"[LLM Error]{str(e)}",False




def fallback_answer(
query:str,
hits:List[Dict]
):


    if len(hits)==0:

        return(
"No relevant content found in uploaded documents."
        )


    output=[]

    output.append(

f"Relevant passages for:\n{query}\n"

    )


    for i,hit in enumerate(
hits,
1
    ):

        meta=hit[
            "metadata"
        ]

        snippet=hit[
            "text"
        ][:250]

        output.append(

f"""
[{i}]
File:
{meta['filename']}

Page:
{meta['page_num']}

{snippet}
"""

        )

    output.append(
"\n⚠️ Ollama unavailable"
    )

    return "\n".join(
        output
    )



def generate_answer(
query:str,
hits:List[Dict]
):


    t0=time.time()


    if len(hits)==0:

        return{

            "answer":
            "No relevant content found in uploaded documents.",

            "sources":[],

            "model_used":
            "none",

            "ollama_available":
            False,

            "latency_ms":
            0
        }


    prompt=build_prompt(
query,
hits
    )


    answer,ok=call_ollama(
prompt
    )


    if not ok or not answer:

        answer=fallback_answer(
query,
hits
        )

        model_used="extractive"

        ollama_available=False

    else:

        model_used=OLLAMA_MODEL

        ollama_available=True


    sources=[]

    seen=set()


    for hit in hits:

        meta=hit[
            "metadata"
        ]

        key=f"""
{meta['filename']}
|
{meta['page_num']}
"""


        if key not in seen:

            seen.add(
                key
            )

            sources.append({

                "filename":
                meta[
                    "filename"
                ],

                "page_num":
                meta[
                    "page_num"
                ],

                "score":
                hit.get(
                    "combined_score",
                    hit.get(
                        "score",
                        0
                    )
                ),

                "snippet":
                hit[
                    "text"
                ][:400]

            })


    latency_ms=int(

        (
            time.time()
            -
            t0
        )*1000

    )


    return{

        "answer":
        answer.strip(),

        "sources":
        sources,

        "model_used":
        model_used,

        "ollama_available":
        ollama_available,

        "latency_ms":
        latency_ms

    }



def check_ollama_status():

    try:

        with httpx.Client(
            timeout=5
        ) as client:

            response=client.get(

f"{OLLAMA_HOST}/api/tags"

            )

            response.raise_for_status()

            models=[

                m["name"]

                for m in

                response.json().get(
                    "models",
                    []
                )

            ]

            return{

                "running":
                True,

                "models":
                models

            }


    except:

        return{

            "running":
            False,

            "models":[]
        }