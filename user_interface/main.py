import streamlit as st
import sys
import os
# Add project root directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ui_components import render_page_header, render_knowledge_base_controls, render_common_questions, render_chat_history, render_input_area, render_sidebar_stats
from chat_manager import initialize_session_state, handle_user_query, process_pending_queries
from knowledge_manager import ensure_knowledge_base_loaded, load_knowledge_base


def main():
    st.set_page_config(
        page_title="RAG Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()

    # Render page header
    render_page_header()
    
    # Automatically load knowledge base (if not already loaded)
    if st.session_state.metadata_store is None or st.session_state.text_index is None or st.session_state.image_index is None:
        with st.spinner("Automatically loading knowledge base, this may take some time (especially first model loading)..."):
            load_knowledge_base()
    else:
        # Ensure knowledge base is loaded (restore state after refresh)
        ensure_knowledge_base_loaded()

    # Get cached KB manager to access embedding handler
    if st.session_state.kb_manager is None:
        try:
            from bot.knowledge_base import KnowledgeBaseManager
            st.session_state.kb_manager = KnowledgeBaseManager()
        except:
            st.session_state.kb_manager = None

    # Only show chat interface when knowledge base is loaded successfully
    if st.session_state.metadata_store is not None and st.session_state.rag_engine is not None:
        # Render knowledge base controls
        render_knowledge_base_controls()
        
        # Render common questions
        render_common_questions()

        # Render chat history
        render_chat_history()

        # Render input area and get input
        query, submitted = render_input_area()
        
        # Handle user query
        if submitted:
            handle_user_query(query)
            
        # Process pending queries - processed after rendering all UI
        # This ensures that even without new submissions, previously accumulated queries are processed
        process_pending_queries()
    else:
        # If knowledge base is not loaded successfully
        render_knowledge_base_controls()
        
        st.info("💡 Please load knowledge base first to start conversation")
        
        # Render common questions
        render_common_questions()

        # Render chat history
        render_chat_history()

        # Render input area and get input
        query, submitted = render_input_area()
        
        # Handle user query
        if submitted:
            handle_user_query(query)
            
        # Process pending queries - processed after rendering all UI
        # This ensures that even without new submissions, previously accumulated queries are processed
        process_pending_queries()

    # Render sidebar statistics
    render_sidebar_stats()


if __name__ == "__main__":
    main()