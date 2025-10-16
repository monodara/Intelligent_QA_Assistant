import streamlit as st
import sys
import os
# 将项目根目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bot.knowledge_base import KnowledgeBaseManager
from bot.config import DOCS_DIR, IMG_DIR
import os
import tempfile
import shutil
from pathlib import Path


def main():
    st.set_page_config(
        page_title="Local RAG - Admin Panel",
        page_icon="📚",
        layout="wide"
    )
    
    # Add clean styling
    st.markdown("""
    <style>
    .main-header {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    .section-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    .upload-area {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px dashed #ced4da;
    }
    .status-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header"><h1>📚 Local RAG - Admin Panel</h1><h3>Knowledge Base Management Tool</h3></div>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### 📁 Upload New Content to Knowledge Base")
    
    # Create two upload areas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Document Files")
        docs_uploaded = st.file_uploader(
            "Drag and drop or click to upload document files (Word, PDF, etc.)",
            type=['docx', 'pdf', 'txt'],
            accept_multiple_files=True,
            key="docs_uploader"
        )
        
        if docs_uploaded:
            st.success(f"Selected {len(docs_uploaded)} document files")
            doc_files = docs_uploaded
        else:
            doc_files = None
    
    with col2:
        st.markdown("#### 🖼️ Image Files")
        img_uploaded = st.file_uploader(
            "Drag and drop or click to upload image files",
            type=['png', 'jpg', 'jpeg', 'bmp', 'gif'],
            accept_multiple_files=True,
            key="img_uploader"
        )
        
        if img_uploaded:
            st.success(f"Selected {len(img_uploaded)} image files")
            img_files = img_uploaded
        else:
            img_files = None
    
    # Select operation type
    st.markdown("### ⚙️ Select Operation Type")
    operation_type = st.radio(
        "Select operation for knowledge base:",
        options=["rebuild", "add"],
        format_func=lambda x: "Rebuild Knowledge Base" if x == "rebuild" else "Incremental Update Knowledge Base",
        horizontal=True
    )
    
    # Execute operation button
    st.markdown("### 🔧 Execute Operation")
    if st.button("🚀 Execute Operation", type="primary", key="execute_btn"):
        if operation_type == "rebuild":
            # Rebuild knowledge base
            with st.spinner("🔄 Rebuilding knowledge base... This may take some time"):
                try:
                    # Process uploaded files
                    if doc_files or img_files:
                        # Create temporary directory to store uploaded files
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # Create temporary document and image directories
                            temp_docs_dir = os.path.join(temp_dir, "docs")
                            temp_img_dir = os.path.join(temp_dir, "images")
                            
                            os.makedirs(temp_docs_dir, exist_ok=True)
                            os.makedirs(temp_img_dir, exist_ok=True)
                            
                            # Save uploaded document files
                            if doc_files:
                                for uploaded_file in doc_files:
                                    file_path = os.path.join(temp_docs_dir, uploaded_file.name)
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                            
                            # Save uploaded image files
                            if img_files:
                                for uploaded_file in img_files:
                                    file_path = os.path.join(temp_img_dir, uploaded_file.name)
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                            
                            # Initialize knowledge base manager and rebuild knowledge base
                            kb_manager = KnowledgeBaseManager()
                            metadata_store, text_index, image_index = kb_manager.build_initial_knowledge_base(temp_docs_dir, temp_img_dir)
                            
                            st.success("✅ Knowledge base rebuilding completed!")
                            st.info(f"📊 Rebuilding result: {len([item for item in metadata_store if item['type'] == 'text'])} text chunks, {len([item for item in metadata_store if item['type'] == 'image'])} images")
                            
                    else:
                        # No new files uploaded, rebuild existing directory knowledge base
                        kb_manager = KnowledgeBaseManager()
                        metadata_store, text_index, image_index = kb_manager.build_initial_knowledge_base(DOCS_DIR, IMG_DIR)
                        
                        st.success("✅ Knowledge base rebuilding completed!")
                        st.info(f"📊 Rebuilding result: {len([item for item in metadata_store if item['type'] == 'text'])} text chunks, {len([item for item in metadata_store if item['type'] == 'image'])} images")
                        
                except Exception as e:
                    st.error(f"❌ Error rebuilding knowledge base: {str(e)}")
                    
        else:  # Incremental update
            with st.spinner("🔄 Incrementally updating knowledge base... This may take some time"):
                try:
                    # Process uploaded files
                    if doc_files or img_files:
                        # Create temporary directory to store uploaded files
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # Create temporary document and image directories
                            temp_docs_dir = os.path.join(temp_dir, "docs")
                            temp_img_dir = os.path.join(temp_dir, "images")
                            
                            os.makedirs(temp_docs_dir, exist_ok=True)
                            os.makedirs(temp_img_dir, exist_ok=True)
                            
                            # Save uploaded document files
                            if doc_files:
                                for uploaded_file in doc_files:
                                    file_path = os.path.join(temp_docs_dir, uploaded_file.name)
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                            
                            # Save uploaded image files
                            if img_files:
                                for uploaded_file in img_files:
                                    file_path = os.path.join(temp_img_dir, uploaded_file.name)
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                                    
                            # Initialize knowledge base manager and incrementally update knowledge base
                            kb_manager = KnowledgeBaseManager()
                            metadata_store, text_index, image_index = kb_manager.add_documents_to_knowledge_base(temp_docs_dir, temp_img_dir)
                            
                            st.success("✅ Knowledge base incremental update completed!")
                            
                    else:
                        # No new files uploaded, update existing directory knowledge base
                        kb_manager = KnowledgeBaseManager()
                        metadata_store, text_index, image_index = kb_manager.add_documents_to_knowledge_base(DOCS_DIR, IMG_DIR)
                        
                        st.success("✅ Knowledge base incremental update completed!")
                        text_count = len([item for item in metadata_store if item['type'] == 'text'])
                        image_count = len([item for item in metadata_store if item['type'] == 'image'])
                        st.info(f"📊 Update result: {text_count} text chunks, {image_count} images")
                        
                except Exception as e:
                    st.error(f"❌ Error incrementally updating knowledge base: {str(e)}")

    # Display current knowledge base status
    st.markdown("### 📊 Current Knowledge Base Status")
    
    if os.path.exists("data/metadata_store.json"):
        try:
            # Directly load metadata without initializing embedding handler
            import json
            with open("data/metadata_store.json", "r", encoding="utf-8") as f:
                metadata_store = json.load(f)
            
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            st.success("✅ Knowledge base loaded")
            text_count = len([item for item in metadata_store if item["type"] == "text"])
            image_count = len([item for item in metadata_store if item["type"] == "image"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-card"><h3>📚 Text Chunks</h3><h2 style="color: #2c3e50; margin: 0;">{}</h2></div>'.format(text_count), unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card"><h3>🖼️ Images</h3><h2 style="color: #2c3e50; margin: 0;">{}</h2></div>'.format(image_count), unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card"><h3>📦 Total Documents</h3><h2 style="color: #2c3e50; margin: 0;">{}</h2></div>'.format(len(metadata_store)), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Cannot load existing knowledge base: {str(e)}")
    else:
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.warning("⚠️ No knowledge base built yet, please rebuild or update knowledge base first")
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()