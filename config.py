import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
PDF_DIR       = os.path.join(BASE_DIR, "..", "data", "pdfs")
CHROMA_DIR    = os.path.join(BASE_DIR, "..", "chroma_data")

# ─── Chunking ─────────────────────────────────────────────────────────────────
CHUNK_SIZE    = 800      # tokens / words per chunk
CHUNK_OVERLAP = 120      # overlap words between consecutive chunks

# ─── Embedding (free, local) ───────────────────────────────────────────────────
EMBED_MODEL   = "all-MiniLM-L6-v2"   # ~80 MB, totally free
EMBED_DIM     = 384

# ─── ChromaDB ─────────────────────────────────────────────────────────────────
COLLECTION_NAME = "rag_documents"

# ─── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K = 3
RERANK_TOP_K = 2

OCR_LANG = "eng"
OCR_DPI = 300
# ─── LLM (Ollama — free, local, no API key) ───────────────────────────────────
OLLAMA_HOST   = "http://localhost:11434"
OLLAMA_MODEL="phi3:mini"          # change to "mistral" or "phi3" if preferred

# ─── OCR ──────────────────────────────────────────────────────────────────────
OCR_LANG      = "eng"       # Tesseract language
OCR_DPI       = 200
