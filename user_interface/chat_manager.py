import streamlit as st
import sys
import os
# 将项目根目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from knowledge_manager import ensure_knowledge_base_loaded

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
    """Generate and process answer"""
    import sys
    import os
    # Add project root directory to Python path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    from bot.rag_engine import RAGEngine
    from bot.knowledge_base import KnowledgeBaseManager
    from bot.config import DOCS_DIR, IMG_DIR
    from bot.ollama_handler import generate_local_answer
    
    with st.spinner("RAG Assistant is thinking..."):
        try:
            print(f"✅ Frontend request has reached backend: {last_user_query}")
            
            # Get knowledge base components
            metadata_store = st.session_state.metadata_store
            text_index = st.session_state.text_index
            image_index = st.session_state.image_index
            
            if metadata_store is None or text_index is None or image_index is None:
                raise Exception("Knowledge base not properly loaded, please load knowledge base first")
            
            # Use embedding handler from cached KB manager to avoid reloading models
            if st.session_state.kb_manager is not None:
                embedding_handler = st.session_state.kb_manager.embedding_handler
            else:
                # If cached KB manager is not available, try to create RAG engine directly
                rag_engine = st.session_state.rag_engine
                if rag_engine is None:
                    rag_engine = RAGEngine()
                    st.session_state.rag_engine = rag_engine
                embedding_handler = rag_engine.embedding_handler
            
            # Text retrieval
            print(f"🔍 Starting text retrieval: {last_user_query[:50]}...")
            query_vec = embedding_handler.get_text_embedding_offline(last_user_query).reshape(1,-1)
            print(f"📊 Query vector shape: {query_vec.shape}")
            
            distances, ids = text_index.search(query_vec, 3)
            print(f"📈 Retrieval results - Distances: {distances}, IDs: {ids}")
            
            retrieved_context = []
            for doc_id in ids[0]:
                if doc_id != -1:
                    match = next((item for item in metadata_store if item["id"]==doc_id), None)
                    if match:
                        retrieved_context.append(match)
                        print(f"📄 Found relevant document ID: {doc_id}, Source: {match.get('source', 'Unknown')}")
            
            # Image retrieval
            if any(keyword in last_user_query.lower() for keyword in ["poster","image","picture","photo","look like","what does it look like"]):
                print(f"🔍 Starting image retrieval...")
                query_vec_img = embedding_handler.get_clip_text_embedding_cpu(last_user_query).reshape(1,-1)
                print(f"📊 Image query vector shape: {query_vec_img.shape}")
                distances, image_ids = image_index.search(query_vec_img, 1)
                print(f"📈 Image retrieval results - Distances: {distances}, IDs: {image_ids}")
                
                for doc_id in image_ids[0]:
                    if doc_id != -1:
                        match = next((item for item in metadata_store if item["id"]==doc_id), None)
                        if match:
                            context_text = f"Related image path: {match['path']}, Image text: '{match['ocr']}'"
                            retrieved_context.append({"type":"image_context","content":context_text,"metadata":match})
                            print(f"🖼️ Found related image ID: {doc_id}, Path: {match['path']}")
            
            # Build Prompt
            context_str = ""
            for i, item in enumerate(retrieved_context):
                content = item.get('content','')
                source = item.get('metadata',{}).get('source', item.get('source','Unknown Source'))
                context_str += f"Background Knowledge {i+1} (Source: {source}):\n{content}\n\n"
            
            print(f"📝 Building Prompt context: {len(context_str)} characters")
            
            from bot.config import SYSTEM_ROLE
            
            prompt = f"""{SYSTEM_ROLE}. Please answer the user's question using a friendly and professional tone based on the following background knowledge. Please only use information from the background knowledge, do not make up information.

[Background Knowledge]
{context_str}
[User Question]
{last_user_query}
"""
            
            print(f"📧 Sending request to Ollama...")
            final_answer = generate_local_answer(prompt)
            
            # Print generated answer information
            print(f"💬 Generated answer: {final_answer[:100]}...")
            
            # Image processing
            image_path_found = None
            for item in retrieved_context:
                if item.get("type")=="image_context":
                    image_path_found = item.get("metadata",{}).get("path")
                    break
            
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
            
            # Redisplay entire chat history to include new reply
            st.rerun()
            
            # Print request processing completion information
            print(f"✅ Backend has processed request and returned answer")
            
        except Exception as e:
            print(f"❌ Error occurred while processing request: {e}")
            import traceback
            print(f"Detailed error information: {traceback.format_exc()}")
            error_msg = f"Answer generation failed: {e}"
            st.error(error_msg)
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            st.rerun()