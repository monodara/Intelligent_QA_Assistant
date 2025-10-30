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
                final_answer = ""
                image_path_found = None
                
                # Extract answer based on tool used
                tool_used = backend_response.get("tool")
                if tool_used == "LLM_direct_answer":
                    final_answer = backend_response.get("answer", "No answer provided.")
                elif tool_used == "get_weather":
                    weather_data = backend_response.get("weather_data", {})
                    if weather_data.get("success"):
                        if weather_data.get("source") == "forecast":
                            final_answer = (
                                f"Weather in {weather_data['location']}, {weather_data['date']}: "
                                f"{weather_data['weather']}. Day Temp: {weather_data['temp_day']}°C, "
                                f"Night Temp: {weather_data['temp_night']}°C, Humidity: {weather_data['humidity']}%, "
                                f"Wind Speed: {weather_data['wind_speed']} m/s."
                            )
                        else: # historical_average
                            final_answer = (
                                f"Historical average weather in {weather_data['location']}, {weather_data['date']}: "
                                f"Typical: {weather_data['typical_weather']}. Avg Temp: {weather_data['avg_temp']}, "
                                f"Avg Humidity: {weather_data['avg_humidity']}. Note: {weather_data['note']}"
                            )
                    else:
                        final_answer = f"Could not retrieve weather: {weather_data.get('error', 'Unknown error')}"
                elif tool_used == "execute_sql_query":
                    final_answer = backend_response.get("answer", "SQL query executed, but no answer provided.")
                    if backend_response.get("data"):
                        final_answer += "\n\nData:\n" + "\n".join([str(row) for row in backend_response["data"][:5]]) # Show first 5 rows
                elif tool_used == "search_knowledge_base":
                    knowledge_results = backend_response.get("knowledge_base_results", [])
                    if knowledge_results:
                        final_answer = "Here's what I found in the knowledge base:\n"
                        for i, item in enumerate(knowledge_results[:3]): # Show top 3 results
                            final_answer += f"Result {i+1} from {item['source']}:\n"
                            final_answer += item["content"][:200] + ("..." if len(item["content"]) > 200 else "") + "\n\n"
                            if item.get("type") == "image" and item.get("path"):
                                image_path_found = item["path"]
                    else:
                        final_answer = "No relevant information found in the knowledge base."
                else:
                    final_answer = backend_response.get("answer", "Unknown tool response.")

                # Add bot reply to history - including image information
                if image_path_found:
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": final_answer,
                        "image_path": image_path_found
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": final_answer
                    })
                
                print(f"✅ Backend processed request, answer: {final_answer[:100]}...")
            else:
                error_msg = f"Backend error: {backend_response.get('error', 'Unknown error')}"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                print(f"❌ Backend error: {error_msg}")
            
            st.rerun()
            
        except Exception as e:
            print(f"❌ Error occurred while processing request: {e}")
            import traceback
            print(f"Detailed error information: {traceback.format_exc()}")
            error_msg = f"Answer generation failed: {e}"
            st.error(error_msg)
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            st.rerun()