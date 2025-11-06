import json
import streamlit as st
import sys
import os
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


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
    if 'just_received_response' not in st.session_state:
        st.session_state.just_received_response = False
    if 'backend_status_checked' not in st.session_state:
        st.session_state.backend_status_checked = False
    if 'backend_is_ready' not in st.session_state:
        st.session_state.backend_is_ready = False

def handle_user_query(query):
    """Handle user query"""
    if query.strip():
        # Print information when frontend request reaches backend
        print(f"✅ Frontend request has reached backend: {query}")
        
        # Add user question to history
        st.session_state.chat_history.append({"role": "user", "content": query})
        # Rerun page to display user message
        st.rerun()  # Rerun page

def process_pending_queries():
    """Process pending user messages"""
    # Only process if we didn't just receive a response in the last cycle
    # to avoid infinite loop after an assistant response was added
    if st.session_state.get('just_received_response', False):
        # Reset the flag after checking
        st.session_state.just_received_response = False
        return

    # If the last message in chat history is from user, it means it's a new query that needs processing
    # Also process if the last message is an error message from assistant to retry
    if st.session_state.chat_history:
        last_message = st.session_state.chat_history[-1]
        if last_message["role"] == "user":
            last_user_query = last_message["content"]
            _generate_and_process_answer(last_user_query)
        elif (last_message["role"] == "assistant" and 
              (last_message["content"].startswith("Answer generation failed") or
               last_message["content"].startswith("❌"))):
            # If last message was an error from assistant, retry the previous user query
            if len(st.session_state.chat_history) >= 2:
                previous_message = st.session_state.chat_history[-2]
                if previous_message["role"] == "user":
                    _generate_and_process_answer(previous_message["content"])

def _generate_and_process_answer(last_user_query):
    """Generate and process answer by calling the backend service"""
    
    with st.spinner("Assistant is thinking..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={"query": last_user_query},
                timeout=120  # Timeout can be adjusted
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Backend returned HTTP {response.status_code}: {response.text}")
            
            backend_response = response.json()
            
            if backend_response.get("success"):
                tool_output_str = backend_response.get("result")
                tool_output = {}

                try:
                    if isinstance(tool_output_str, str):
                        tool_output = json.loads(tool_output_str)
                    elif isinstance(tool_output_str, dict):
                        tool_output = tool_output_str
                except (json.JSONDecodeError, TypeError):
                    # For map tool responses (and potentially other tools), the result might already be a processed answer string
                    # In this case, treat it as a successful response with the string as the answer
                    tool_output = {"success": True, "answer": str(tool_output_str)}

                if tool_output.get("success"):
                    final_answer = tool_output.get("answer", "The tool ran successfully but provided no answer.")

                    image_path_found = None
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

                else:
                    error_msg = f"The assistant tried to use a tool, but it failed: {tool_output.get('error', 'Unknown tool error')}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

            else:
                error_msg = f"Backend error: {backend_response.get('error', 'Unknown error')}"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            
        except Exception as e:
            print(f"❌ Error occurred while processing request: {e}")
            import traceback
            print(f"Detailed error information: {traceback.format_exc()}")
            error_msg = f"Answer generation failed: {e}"
            st.error(error_msg)
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

    # Set flag to indicate we just received a response to prevent reprocessing
    st.session_state.just_received_response = True
    # Rerun page to update UI
    st.rerun()