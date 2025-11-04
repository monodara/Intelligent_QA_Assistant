import streamlit as st

def get_theme_styles():
    """Return modern-themed CSS styles"""
    return """
    <style>
        /* Global styles */
        .main-header {
            text-align: center;
            color: #2c3e50;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 30px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            color: white;
        }
        .main-header h1 {
            font-size: 2.5em;
            margin-bottom: 0.3em;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .main-header p {
            font-size: 1.2em;
            color: #ecf0f1;
            font-style: italic;
            margin: 0;
        }
        .question-input {
            padding: 25px;
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        .answer-output {
            padding: 20px;
            background: linear-gradient(to right, #ffffff, #f8f9fa);
            border-radius: 15px;
            margin: 20px 0;
            border-left: 5px solid #11998e;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        .modern-theme {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        .modern-theme h2 {
            margin: 0;
            font-size: 1.8em;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .user-message {
            text-align: right; 
            margin: 15px 0;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user-bubble {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 15px 20px; 
            border-radius: 20px; 
            display: inline-block; 
            max-width: 80%;
            border-top-right-radius: 5px;
            box-shadow: 0 5px 15px rgba(17, 153, 142, 0.3);
        }
        .assistant-message {
            text-align: left; 
            margin: 15px 0;
            animation: fadeIn 0.3s ease-in;
        }
        .assistant-bubble {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            color: #2c3e50;
            padding: 15px 20px; 
            border-radius: 20px; 
            display: inline-block; 
            max-width: 80%;
            border-top-left-radius: 5px;
            box-shadow: 0 5px 15px rgba(168, 237, 234, 0.3);
        }
        .common-questions {
            background: linear-gradient(to right, #e6ffea, #d4f8e8);
            padding: 20px;
            border-radius: 15px;
            margin: 15px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        .modern-button {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
            color: white; 
            border: none; 
            padding: 12px 25px; 
            border-radius: 30px; 
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(17, 153, 142, 0.4);
        }
        .modern-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(17, 153, 142, 0.6);
        }
        .modern-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin: 15px 0;
            border: 1px solid #e9ecef;
        }
        .chat-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            max-height: 60vh;
            overflow-y: auto;
        }
        .input-area {
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        .stats-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 5px 15px rgba(17, 153, 142, 0.3);
        }
        .question-tag {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            border: none;
            padding: 12px 18px;
            border-radius: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 5px;
            display: inline-block;
            box-shadow: 0 3px 10px rgba(17, 153, 142, 0.2);
            text-align: center;
            min-width: 120px;
            max-width: 250px;
            white-space: normal;
            word-wrap: break-word;
            line-height: 1.4;
        }
        .question-tag:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(17, 153, 142, 0.4);
        }
    </style>
    """

def render_page_header():
    """Render page header"""
    from bot.config import SYSTEM_NAME
    st.markdown(get_theme_styles(), unsafe_allow_html=True)
    st.markdown(f'<div class="modern-theme"><h2>🤖 {SYSTEM_NAME} 🤖</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-header"><h1>✨ Welcome to Use {SYSTEM_NAME} ✨</h1></div>', unsafe_allow_html=True)

def render_knowledge_base_controls():
    """Render knowledge base control buttons"""
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Reload Knowledge Base", type="secondary", key="chat_reload_kb"):
            from knowledge_manager import load_knowledge_base
            if load_knowledge_base():
                st.session_state.chat_history = []  # Clear chat history
    
    with col1:
        if st.session_state.get('metadata_store') is not None:
            st.success("✅ Knowledge Base Loaded")

def render_common_questions():
    """Render common questions section"""
    st.markdown("### 💭 Quick Common Questions")
    common_questions = [
        "Please introduce this domain?",
        "What are the important things to note?",
        "Recommend some related resources",
        "What are common questions?",
        "What are the latest updates?"
    ]
    
    # Simple implementation: display questions as buttons in a scrollable container
    with st.expander("View Common Questions", expanded=True):
        # Create buttons for each question
        for i, question in enumerate(common_questions):
            if st.button(f"🏷️ {question}", key=f"quick_question_{i}", 
                        help=question,
                        type="secondary"):
                st.session_state.temp_question = question
                st.rerun()

def render_chat_history():
    """Render chat history"""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown("### 🗨️ Chat History")
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'<div class="user-message"><div class="user-bubble">👤 You: {chat["content"]}</div></div>', unsafe_allow_html=True)
            else:
                # Display assistant response
                from bot.config import SYSTEM_NAME
                st.markdown(f'<div class="assistant-message"><div class="assistant-bubble">🤖 {SYSTEM_NAME}: {chat["content"]}</div></div>', unsafe_allow_html=True)
                # Display related images if any
                if "image_path" in chat and chat["image_path"]:
                    try:
                        # Display retrieved images
                        from PIL import Image
                        import os
                        if os.path.exists(chat["image_path"]):
                            st.image(chat["image_path"], caption="Related Image", width='stretch')
                        else:
                            st.warning(f"Image file does not exist: {chat['image_path']}")
                    except Exception as img_error:
                        st.warning(f"Cannot display image: {chat['image_path']}")
    st.markdown('</div>', unsafe_allow_html=True)

def render_input_area():
    """Render input area"""
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    st.markdown("### 📝 Enter your question")
    
    # Use form to enable automatic clearing after submission
    with st.form(key="question_form", clear_on_submit=True):
        query = st.text_input("Please enter your question:", key="query_input_form", placeholder="Type your question here...")
        col1, col2 = st.columns([1, 8])
        with col1:
            submitted = st.form_submit_button("🚀 Send", type="primary")
        with col2:
            if st.form_submit_button("🗑️ Clear Chat", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
    
    # Check for pending queries (common questions)
    # Note: Common questions are already set to pending_query at button click, no need to check temp_question additionally
    if 'pending_query' in st.session_state and st.session_state.pending_query:
        query = st.session_state.pending_query
        st.session_state.pending_query = None  # Clear pending query
        submitted = True
    elif 'temp_question' in st.session_state and st.session_state.temp_question:
        query = st.session_state.temp_question
        st.session_state.temp_question = None  # Clear temporary storage
        st.session_state.pending_query = query  # Set pending query
        submitted = True
        st.rerun()  # Rerun to ensure processing
    
    st.markdown('</div>', unsafe_allow_html=True)
    return query, submitted

def render_sidebar_stats():
    """Render sidebar statistics"""
    if st.session_state.metadata_store is not None:
        st.sidebar.markdown("### 📊 Knowledge Base Information")
        text_count = len([item for item in st.session_state.metadata_store if item["type"] == "text"])
        image_count = len([item for item in st.session_state.metadata_store if item["type"] == "image"])
        total_count = len(st.session_state.metadata_store)
        
        # Display statistics in modern card style
        st.sidebar.markdown(
            f"""
            <div class="stats-card">
                <h4>📚 Text Chunks</h4>
                <h2 style="color: white; margin: 0;">{text_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.sidebar.markdown(
            f"""
            <div class="stats-card">
                <h4>🖼️ Images</h4>
                <h2 style="color: white; margin: 0;">{image_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.sidebar.markdown(
            f"""
            <div class="stats-card">
                <h4>📦 Total Documents</h4>
                <h2 style="color: white; margin: 0;">{total_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Display knowledge base status
        st.sidebar.success("✅ Knowledge Base Running Normally")