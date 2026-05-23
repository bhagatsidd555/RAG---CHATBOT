"""
main.py
FastAPI backend for RAG Chatbot
Free stack:
Sentence-transformers
ChromaDB
Ollama
"""

import sys
import os
import shutil
import time

sys.path.insert(
    0,
    os.path.dirname(__file__)
)

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List, Optional

from config import PDF_DIR

from ingestion.pdf_extractor import extract_pdf
from ingestion.preprocessor import clean_text
from ingestion.chunker import create_chunks

from embeddings.embedder import (
    embed_texts
)

from vectordb.chroma_db import (

    add_chunks,
    get_all_documents,
    collection_count,
    delete_collection

)

from retrieval.retriever import retrieve

from generation.generator import (

    generate_answer,
    check_ollama_status

)

from evaluation.metrics import (

    record,
    get_stats

)


os.makedirs(
    PDF_DIR,
    exist_ok=True
)

app=FastAPI(

    title="RAG Chatbot API",

    version="2.0"

)


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_methods=["*"],

    allow_headers=["*"]

)


# ==========================
# FRONTEND
# ==========================

FRONTEND_DIR=os.path.join(

    os.path.dirname(__file__),

    "..",

    "frontend"

)


if os.path.exists(
    FRONTEND_DIR
):

    app.mount(

        "/static",

        StaticFiles(
            directory=FRONTEND_DIR
        ),

        name="static"

    )


@app.get("/")
def serve_ui():

    index=os.path.join(

        FRONTEND_DIR,

        "index.html"

    )

    if os.path.exists(index):

        return FileResponse(
            index
        )

    return {

        "message":
        "RAG backend running"

    }


# ==========================
# MODELS
# ==========================


class QueryRequest(
    BaseModel
):

    query:str

    top_k:Optional[
        int
    ]=6

    rerank_top_k:Optional[
        int
    ]=4



class QueryResponse(
    BaseModel
):

    answer:str

    sources:list

    retrieved_chunks:list

    latency_ms:int

    retrieval_latency_ms:int

    generation_latency_ms:int

    ollama_available:bool

    model_used:str

    metrics:dict



# ==========================
# INGESTION
# ==========================


ingestion_status={

"running":False,

"progress":0,

"total":0,

"current_file":"",

"done":False,

"error":None,

"chunks_added":0

}


def run_ingestion(
pdf_paths
):


    global ingestion_status


    ingestion_status.update({

        "running":True,

        "progress":0,

        "total":len(
            pdf_paths
        ),

        "done":False,

        "error":None,

        "chunks_added":0

    })


    try:


        all_chunks=[]


        for i,path in enumerate(
            pdf_paths
        ):


            fname=os.path.basename(
                path
            )

            ingestion_status[
                "current_file"
            ]=fname


            ingestion_status[
                "progress"
            ]=i


            pages=extract_pdf(
                path
            )


            for p in pages:

                p["text"]=clean_text(

                    p["text"]

                )


            pages=[

                p

                for p in pages

                if len(

                    p["text"]

                    .strip()

                )>50
            ]


            chunks=create_chunks(
                pages
            )


            all_chunks.extend(
                chunks
            )


        if all_chunks:


            texts=[

                c["text"]

                for c in all_chunks
            ]


            embeddings=embed_texts(
                texts
            )


            add_chunks(

                all_chunks,

                embeddings

            )


            ingestion_status[
                "chunks_added"
            ]=len(
                all_chunks
            )


        ingestion_status.update({

            "running":False,

            "done":True

        })


    except Exception as e:


        ingestion_status.update({

            "running":False,

            "done":True,

            "error":str(e)

        })



# ==========================
# ENDPOINTS
# ==========================


@app.get("/api/status")
def status():

    return{

        "chunks_in_db":
        collection_count(),

        "documents":
        get_all_documents(),

        "ollama":
        check_ollama_status(),

        "ingestion":
        ingestion_status
    }



@app.get("/api/metrics")
def metrics():

    return get_stats()



@app.post(
"/api/ingest/upload"
)

async def upload_ingest(

background_tasks:
BackgroundTasks,

files:List[
UploadFile
]=File(...)

):


    saved=[]


    for f in files:


        if not f.filename.lower(

        ).endswith(

            ".pdf"
        ):

            continue


        dest=os.path.join(

            PDF_DIR,

            f.filename
        )


        with open(

            dest,

            "wb"

        ) as out:

            shutil.copyfileobj(

                f.file,

                out
            )


        saved.append(
            dest
        )


    if len(saved)==0:

        raise HTTPException(

            400,

            "No PDFs uploaded"

        )


    background_tasks.add_task(

        run_ingestion,

        saved

    )


    return{

        "message":

        f"Started ingestion:{len(saved)}"

    }



@app.post(
"/api/query",
response_model=QueryResponse
)

def query_rag(
req:QueryRequest
):


    if not req.query.strip():

        raise HTTPException(

            400,

            "Empty query"

        )


    if collection_count()==0:

        raise HTTPException(

            400,

            "No PDFs ingested"

        )


    t0=time.time()


    retrieval=retrieve(

        req.query,

        req.top_k,

        req.rerank_top_k

    )


    hits=retrieval[
        "hits"
    ]


    retrieval_ms=retrieval[
        "latency_ms"
    ]


    gen=generate_answer(

        req.query,

        hits
    )


    generation_ms=gen[
        "latency_ms"
    ]


    total_ms=int(

        (
            time.time()
            -
            t0
        )*1000
    )


    score=0

    if hits:

        score=hits[0].get(

            "combined_score",

            0

        )


    record(

        total_ms,

        score,

        gen[
            "ollama_available"
        ]

    )


    retrieved=[

        {

            "rank":
            i+1,

            "text":
            h["text"][:500],

            "filename":
            h["metadata"]["filename"],

            "page_num":
            h["metadata"]["page_num"],

            "score":
            h.get(
                "combined_score",
                h["score"]
            )

        }

        for i,h in enumerate(
            hits
        )

    ]


    return QueryResponse(

        answer=gen["answer"],

        sources=gen["sources"],

        retrieved_chunks=retrieved,

        latency_ms=total_ms,

        retrieval_latency_ms=retrieval_ms,

        generation_latency_ms=generation_ms,

        ollama_available=gen[
            "ollama_available"
        ],

        model_used=gen[
            "model_used"
        ],

        metrics=get_stats()

    )


@app.delete("/api/reset")
def reset():

    delete_collection()

    return{

        "message":
        "DB cleared"

    }


if __name__=="__main__":

    import uvicorn

    uvicorn.run(

        "main:app",

        host="0.0.0.0",

        port=8000,

        reload=True

    )