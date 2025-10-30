import os

# ---------------- Global Configuration ----------------
# Default configuration, can be overridden via environment variables or parameters
DOCS_DIR = os.getenv("DOCS_DIR", "knowledge_base")
IMG_DIR = os.path.join(DOCS_DIR, "images")
DATA_DIR = os.getenv("DATA_DIR", "data")
TEXT_FAISS_FILE = os.path.join(DATA_DIR, "text_index.index")
IMAGE_FAISS_FILE = os.path.join(DATA_DIR, "image_index.index")
METADATA_FILE = os.path.join(DATA_DIR, "metadata_store.json")

IMAGE_EMBEDDING_DIM = 512

# Model configuration
TEXT_EMBEDDING_MODEL = os.getenv("TEXT_EMBEDDING_MODEL", 'all-MiniLM-L6-v2')
CLIP_MODEL_NAME = os.getenv("CLIP_MODEL_NAME", "openai/clip-vit-base-patch32")

# Ollama model configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))

# Retrieval configuration
DEFAULT_RETRIEVAL_K = int(os.getenv("DEFAULT_RETRIEVAL_K", "7"))

# System name configuration
SYSTEM_NAME = os.getenv("SYSTEM_NAME", "Local RAG Assistant")
SYSTEM_ROLE = os.getenv("SYSTEM_ROLE", "You are a professional assistant of a theme park.")