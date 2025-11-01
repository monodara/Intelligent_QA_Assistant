import json
import streamlit as st
import sys
import os
# 将项目根目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from knowledge_manager import ensure_knowledge_base_loaded
from bot.api_service import handle_chat_query # Import the backend service function

def initialize_session_state():
    """Initialize session state"""
    if 'metadata_store' not in st.session_state:
        st.session_state.metadata_store = None
    if 'text_index' not in st.session_state:
        st.session_state.text_index = None
    if 'image_index' not in st.session_state:
        st.session_state.image_index = None
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'kb_manager' not in st.session_state:
        st.session_state.kb_manager = None
    if 'should_clear_input' not in st.session_state:
        st.session_state.should_clear_input = False
    if 'temp_question' not in st.session_state:
        st.session_state.temp_question = None
    if 'pending_query' not in st.session_state:
        st.session_state.pending_query = None

def handle_user_query(query):
    """Handle user query"""
    if query.strip():
        # Print information when frontend request reaches backend
        print(f"✅ Frontend request has reached backend: {query}")
        
        # Add user question to history
        st.session_state.chat_history.append({"role": "user", "content": query})
        # Rerun page to display user message, but don't clear input immediately (form handles it automatically)
        st.rerun()  # Rerun page

def process_pending_queries():
    """Process pending user messages"""
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        last_user_query = st.session_state.chat_history[-1]["content"]
        # Check if there is already a corresponding assistant reply
        # If chat history length is less than 2, or last one is not assistant reply, need to process
        if len(st.session_state.chat_history) < 2:
            _generate_and_process_answer(last_user_query)
        else:
            last_but_one = st.session_state.chat_history[-2]
            # Process if last is user message and second-to-last is not assistant reply or is error message
            if (last_but_one["role"] != "assistant" or
                last_but_one["content"].startswith("Answer generation failed") or
                last_but_one["content"].startswith("❌")):
                _generate_and_process_answer(last_user_query)

def _generate_and_process_answer(last_user_query):
    """Generate and process answer by calling the backend service"""
    
    with st.spinner("RAG Assistant is thinking..."):
        try:
            print(f"✅ Frontend sending query to backend: {last_user_query}")
            
            # Call the backend service to handle the query
            backend_response = handle_chat_query(last_user_query)
            
            if backend_response.get("success"):
                tool_output_str = backend_response.get("result")
                tool_output = {}

                try:
                    if isinstance(tool_output_str, str):
                        tool_output = json.loads(tool_output_str)
                    elif isinstance(tool_output_str, dict):
                        tool_output = tool_output_str
                except (json.JSONDecodeError, TypeError):
                    tool_output = {"success": False, "error": str(tool_output_str)}

                if tool_output.get("success"):
                    final_answer = tool_output.get("answer", "The tool ran successfully but provided no answer.")
                    
                    image_path_found = None
                    # For RAG tool, check for an image in the source results
                    if backend_response.get("tool") == "search_knowledge_base":
                        source_results = tool_output.get("results", [])
                        for item in source_results:
                            if item.get("type") == "image" and item.get("path"):
                                image_path_found = item["path"]
                                break
                    
                    message_to_append = {"role": "assistant", "content": final_answer}
                    if image_path_found:
                        message_to_append["image_path"] = image_path_found
                    st.session_state.chat_history.append(message_to_append)

                else: # The tool call itself failed
                    error_msg = f"The assistant tried to use a tool, but it failed: {tool_output.get('error', 'Unknown tool error')}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

            else: # The backend router failed
                error_msg = f"Backend error: {backend_response.get('error', 'Unknown error')}"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            
            st.rerun()
            
        except Exception as e:
            print(f"❌ Error occurred while processing request: {e}")
            import traceback
            print(f"Detailed error information: {traceback.format_exc()}")
            error_msg = f"Answer generation failed: {e}"
            st.error(error_msg)
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            st.rerun()