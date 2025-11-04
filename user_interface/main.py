import streamlit as st
import sys
import os
# Add project root directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ui_components import render_page_header, render_knowledge_base_controls, render_common_questions, render_chat_history, render_input_area, render_sidebar_stats
from chat_manager import initialize_session_state, handle_user_query, process_pending_queries
from knowledge_manager import ensure_backend_ready, load_knowledge_base, get_kb_status


def main():
    st.set_page_config(
        page_title="Intelligent Q&A Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()

    # Render page header
    render_page_header()
    
    # Check if backend is ready (no automatic loading on every refresh)
    backend_ready = ensure_backend_ready()

    # Check knowledge base status
    kb_status = get_kb_status() if backend_ready else {"is_loaded": False, "error": "Backend not accessible"}
    
    # Only show chat interface when knowledge base is loaded successfully
    if kb_status.get("is_loaded"):
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
        
        if not backend_ready:
            st.error("❌ Backend service is not accessible. Please make sure the FastAPI server is running.")
        else:
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