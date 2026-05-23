# 📚 RAG Chatbot with OCR + Hybrid Retrieval + Ollama

A fully local PDF Knowledge Base Chatbot built using Retrieval-Augmented Generation (RAG). The system supports PDF ingestion, OCR for scanned documents, hybrid retrieval (semantic + BM25), local LLM inference using Ollama, and real-time evaluation metrics.

---

##  Features

✅ PDF Upload & Ingestion  
✅ PDF Text Extraction (PyMuPDF)  
✅ OCR Support for Scanned PDFs (Tesseract)  
✅ Text Preprocessing & Chunking  
✅ Sentence Transformer Embeddings  
✅ ChromaDB Vector Storage  
✅ Hybrid Retrieval (Vector Search + BM25 Reranking)  
✅ Local LLM using Ollama (No API key required)  
✅ Source Citations  
✅ Latency Metrics Dashboard  
✅ Retrieval Score Tracking  
✅ Hallucination Reduction  
✅ Fully Local & Free Stack  

---

##  Project Architecture

```text
PDF Upload
    ↓
PDF Extraction
    ↓
OCR (for scanned PDFs)
    ↓
Preprocessing
    ↓
Chunking
    ↓
Embeddings
    ↓
ChromaDB Storage
    ↓
Query Embedding
    ↓
Hybrid Retrieval
    ↓
BM25 Re-ranking
    ↓
Ollama LLM
    ↓
Generated Answer + Sources
```

---

##  Project Structure

```text
rag-chatbot/
│
├── backend/
│   │
│   ├── embeddings/
│   │   └── embedder.py
│   │
│   ├── ingestion/
│   │   ├── pdf_extractor.py
│   │   ├── chunker.py
│   │   └── preprocessor.py
│   │
│   ├── retrieval/
│   │   └── retriever.py
│   │
│   ├── generation/
│   │   └── generator.py
│   │
│   ├── evaluation/
│   │   └── metrics.py
│   │
│   ├── vectordb/
│   │   └── chroma_db.py
│   │
│   ├── config.py
│   └── main.py
│
├── frontend/
│
├── data/
│   └── pdfs/
│
├── requirements.txt
├── run.sh
├── run.bat
└── README.md
```

---

##  Tech Stack

### Backend

- FastAPI
- Python

### Frontend

- HTML
- CSS
- JavaScript

### Embeddings

- Sentence Transformers
- all-MiniLM-L6-v2

### Vector Database

- ChromaDB
- HNSW Index

### Retrieval

- Hybrid Retrieval
- BM25 Re-ranking

### OCR

- Tesseract OCR
- PyMuPDF

### LLM

- Ollama
- Phi3 Mini / Llama3

---

##  Installation

Clone repository:

```bash
git clone https://github.com/YOUR_USERNAME/rag-chatbot.git

cd rag-chatbot
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

### Mac/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Install Ollama

Download:

https://ollama.com/download

Pull model:

```bash
ollama pull phi3:mini
```

or

```bash
ollama pull llama3
```

Start Ollama:

```bash
ollama serve
```

---

##  Run Project

Start backend:

```bash
cd backend

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open browser:

```text
http://localhost:8000
```

---

## Using the Chatbot

### Upload PDFs

Click:

```text
Choose PDFs
```

then:

```text
Upload & Ingest
```

---

### Ask Questions

Examples:

```text
Explain CNN architecture

What is overfitting?

Difference between CNN and RNN

Explain machine learning lifecycle

How can hallucinations be reduced in RAG systems?
```

---

## Metrics Dashboard

Tracks:

- Query Count
- p50 Latency
- p95 Latency
- Average Retrieval Score
- Ollama Availability

Example:

```text
Queries: 20

p50: 3200ms

p95: 4700ms

Average Score: 0.72
```

---

## OCR Support

Scanned PDFs automatically use OCR:

```text
Native PDF
    ↓
Direct text extraction

Scanned PDF
    ↓
Tesseract OCR
```

---

## Future Improvements

- User authentication
- Multi-user support
- Streaming responses
- Docker deployment
- Kubernetes deployment
- Redis caching
- Multi-modal support

---

## 📸 Screenshots

Add screenshots here:

```text
screenshots/home.png

screenshots/chat.png

screenshots/metrics.png
```


## If you like this project

Give it a star on GitHub