import json
from typing import Dict, Any

from .core.knowledge_base import KnowledgeBaseManager
from .core.rag_engine import RAGEngine
from .core.query_router import QueryRouter
from .config import DOCS_DIR, IMG_DIR

# Global instances to avoid re-initialization across requests in a long-running process
# In a real web service, this would be managed by the web framework's lifecycle
_kb_manager: KnowledgeBaseManager = None
_rag_engine: RAGEngine = None
_query_router: QueryRouter = None
_metadata_store = None
_text_index = None
_image_index = None

def _initialize_backend_components():
    """Initializes or re-initializes backend components if they are not set."""
    global _kb_manager, _rag_engine, _query_router, _metadata_store, _text_index, _image_index

    if _kb_manager is None:
        print("Initializing KnowledgeBaseManager in backend service...")
        _kb_manager = KnowledgeBaseManager()
        _metadata_store, _text_index, _image_index = _kb_manager.build_or_load_knowledge_base(DOCS_DIR, IMG_DIR)
        print("Knowledge base loaded in backend service.")

    if _rag_engine is None:
        print("Initializing RAGEngine in backend service...")
        _rag_engine = RAGEngine()

    if _query_router is None:
        print("Initializing QueryRouter in backend service...")
        # Pass the already loaded components to the QueryRouter
        _query_router = QueryRouter(_rag_engine, _metadata_store, _text_index, _image_index)
        print("QueryRouter initialized in backend service.")

def handle_chat_query(query: str) -> Dict[str, Any]:
    """
    Handles a chat query from the frontend by routing it through the QueryRouter.
    This function acts as the backend API endpoint for chat interactions.
    """
    _initialize_backend_components() # Ensure components are initialized

    if _query_router is None:
        return {
            "success": False,
            "tool": "system_error",
            "error": "Backend components failed to initialize."
        }

    print(f"Backend service received query: {query}")
    result = _query_router.route_query(query)
    print(f"Backend service returning result: {result}")
    return result

# Example of how to expose a knowledge base reload function if needed
def reload_knowledge_base_backend() -> Dict[str, Any]:
    """
    Reloads the knowledge base components.
    """
    global _kb_manager, _rag_engine, _query_router, _metadata_store, _text_index, _image_index
    print("Reloading knowledge base in backend service...")
    _kb_manager = KnowledgeBaseManager()
    _metadata_store, _text_index, _image_index = _kb_manager.build_or_load_knowledge_base(DOCS_DIR, IMG_DIR)
    _rag_engine = RAGEngine()
    _query_router = QueryRouter(_rag_engine, _metadata_store, _text_index, _image_index)
    print("Knowledge base reloaded in backend service.")
    return {"success": True, "message": "Knowledge base reloaded successfully."}
