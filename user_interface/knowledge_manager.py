import streamlit as st
import sys
import os
# 将项目根目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bot.rag_engine import RAGEngine
from bot.knowledge_base import KnowledgeBaseManager
from bot.config import DOCS_DIR, IMG_DIR

@st.cache_resource(show_spinner=False)
def get_cached_components():
    """Use cached components to avoid reloading"""
    print("🔄 Initializing all components (including Embedding and CLIP models)...")
    kb_manager = KnowledgeBaseManager()
    metadata_store, text_index, image_index = kb_manager.build_or_load_knowledge_base(DOCS_DIR, IMG_DIR)
    rag_engine = RAGEngine()
    print("✅ All components initialized!")
    return kb_manager, metadata_store, text_index, image_index, rag_engine


def load_knowledge_base():
    """Load knowledge base - Use cached version"""
    with st.spinner("Loading knowledge base..."):
        try:
            kb_manager, metadata_store, text_index, image_index, rag_engine = get_cached_components()
            
            # Store components to session state
            st.session_state.kb_manager = kb_manager
            st.session_state.metadata_store = metadata_store
            st.session_state.text_index = text_index
            st.session_state.image_index = image_index
            st.session_state.rag_engine = rag_engine
            
            st.success("Knowledge base loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Knowledge base loading failed: {e}")
            st.error(f"Knowledge base loading failed: {e}")
            return False


def ensure_knowledge_base_loaded():
    """Ensure knowledge base is loaded, prioritize cached resources"""
    if ('kb_manager' in st.session_state and 
        st.session_state.metadata_store is not None and 
        st.session_state.text_index is not None and 
        st.session_state.image_index is not None and
        st.session_state.rag_engine is not None):
        return True
    
    # Get components from cache
    try:
        kb_manager, metadata_store, text_index, image_index, rag_engine = get_cached_components()
        
        # Store to session state
        st.session_state.kb_manager = kb_manager
        st.session_state.metadata_store = metadata_store
        st.session_state.text_index = text_index
        st.session_state.image_index = image_index
        st.session_state.rag_engine = rag_engine
        
        return True
    except Exception as e:
        print(f"❌ Failed to ensure knowledge base loading: {e}")
        return False