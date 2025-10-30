import streamlit as st
import sys
import os
# 将项目根目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bot.api_service import _initialize_backend_components, reload_knowledge_base_backend, _kb_manager, _metadata_store, _text_index, _image_index

@st.cache_resource(show_spinner=False)
def get_cached_backend_status():
    """
    Use cached status to avoid re-initializing backend components unnecessarily.
    This function triggers the backend initialization.
    """
    print("🔄 Triggering backend component initialization...")
    try:
        _initialize_backend_components()
        print("✅ Backend components initialized!")
        return True
    except Exception as e:
        print(f"❌ Backend component initialization failed: {e}")
        return False


def load_knowledge_base():
    """
    Load or reload knowledge base by calling the backend service.
    """
    with st.spinner("Loading knowledge base..."):
        try:
            # Trigger backend initialization/reload
            result = reload_knowledge_base_backend()
            if result.get("success"):
                st.success("Knowledge base loaded successfully!")
                return True
            else:
                st.error(f"Knowledge base loading failed: {result.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Knowledge base loading failed: {e}")
            st.error(f"Knowledge base loading failed: {e}")
            return False


def ensure_knowledge_base_loaded():
    """
    Ensure backend components are initialized and knowledge base is loaded.
    """
    # Check if backend components are already initialized
    if _metadata_store is not None and _text_index is not None and _image_index is not None:
        return True
    
    # If not, try to initialize them via the cached function
    try:
        return get_cached_backend_status()
    except Exception as e:
        print(f"❌ Failed to ensure knowledge base loading: {e}")
        return False

# Expose backend status for UI components
def get_kb_status():
    return {
        "metadata_store_count": len(_metadata_store) if _metadata_store else 0,
        "text_index_count": _text_index.ntotal if _text_index else 0,
        "image_index_count": _image_index.ntotal if _image_index else 0,
        "is_loaded": _metadata_store is not None and _text_index is not None and _image_index is not None
    }