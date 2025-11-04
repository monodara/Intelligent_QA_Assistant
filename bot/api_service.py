# bot/api_service.py
import os
from typing import Dict, Any
from .core.knowledge_base import KnowledgeBaseManager
from .core.rag_engine import RAGEngine
from .core.query_router import QueryRouter
from .config import DOCS_DIR, IMG_DIR

# 全局对象（只在服务启动时初始化一次）
_kb_manager: KnowledgeBaseManager = None
_rag_engine: RAGEngine = None
_query_router: QueryRouter = None
_metadata_store = None
_text_index = None
_image_index = None


def initialize_backend_components():
    """Initialize backend components once."""
    global _kb_manager, _rag_engine, _query_router, _metadata_store, _text_index, _image_index

    if _kb_manager is None:
        print("🔧 Initializing KnowledgeBaseManager...")
        _kb_manager = KnowledgeBaseManager()
        _metadata_store, _text_index, _image_index = _kb_manager.build_or_load_knowledge_base(DOCS_DIR, IMG_DIR)

    if _rag_engine is None:
        print("🔧 Initializing RAGEngine...")
        _rag_engine = RAGEngine()

    if _query_router is None:
        print("🔧 Initializing QueryRouter...")
        _query_router = QueryRouter(
            rag_engine=_rag_engine,
            metadata_store=_metadata_store,
            text_index=_text_index,
            image_index=_image_index
        )
        print("✅ QueryRouter ready.")


def handle_chat_query(query: str) -> Dict[str, Any]:
    """Main backend API logic."""

    print(f"💬 Received query: {query}")
    if not _query_router:
        return {"success": False, "error": "QueryRouter not initialized."}

    result = _query_router.route_query(query)
    print(f"🧠 Returning result: {result}")
    return result


def reload_knowledge_base() -> Dict[str, Any]:
    """Optional: reload knowledge base manually"""
    global _kb_manager, _rag_engine, _query_router, _metadata_store, _text_index, _image_index

    print("♻️ Reloading knowledge base...")
    _kb_manager = KnowledgeBaseManager()
    _metadata_store, _text_index, _image_index = _kb_manager.build_or_load_knowledge_base(DOCS_DIR, IMG_DIR)
    _rag_engine = RAGEngine()
    _query_router = QueryRouter(
        rag_engine=_rag_engine,
        metadata_store=_metadata_store,
        text_index=_text_index,
        image_index=_image_index
    )
    return {"success": True, "message": "Knowledge base reloaded successfully."}
