import os
import json
import numpy as np
import faiss
from ..config import (
    TEXT_FAISS_FILE, IMAGE_FAISS_FILE, METADATA_FILE,
    IMAGE_EMBEDDING_DIM, DOCS_DIR, IMG_DIR
)
from .document_parser import parse_document, get_all_files_in_directory
from .embedding_handler import EmbeddingHandler


class KnowledgeBaseManager:
    def __init__(self):
        self.embedding_handler = EmbeddingHandler()
        self.TEXT_EMBEDDING_DIM = self.embedding_handler.TEXT_EMBEDDING_DIM

    def load_existing_knowledge_base(self):
        """
        Load existing knowledge base
        """
        print("Loading local FAISS index and metadata_store...")
        text_index_map = faiss.read_index(TEXT_FAISS_FILE)
        image_index_map = faiss.read_index(IMAGE_FAISS_FILE)
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            metadata_store = json.load(f)
        print("FAISS index and metadata_store loaded successfully.")
        return metadata_store, text_index_map, image_index_map

    def build_initial_knowledge_base(self, docs_dir=DOCS_DIR, img_dir=IMG_DIR):
        """
        Build initial knowledge base
        """
        print("\n--- Building Initial Knowledge Base ---")
        metadata_store = []
        text_vectors = []
        image_vectors = []
        doc_id_counter = 0

        # Recursively get all document files
        doc_files = get_all_files_in_directory(docs_dir, ['.docx', '.pdf', '.txt'])
        print(f"Found {len(doc_files)} document files")

        # Document vectorization
        for file_path in doc_files:
            filename = os.path.basename(file_path)
            print(f"Processing document: {file_path}")
            chunks = parse_document(file_path)
            for chunk in chunks:
                # Save relative path as source information for easy file location tracking
                relative_path = os.path.relpath(file_path, start=docs_dir)
                metadata = {"id": doc_id_counter, "source": relative_path, "page": 1}
                if chunk["type"] in ["text", "table"]:
                    text = chunk["content"]
                    if not text.strip():
                        continue
                    metadata["type"] = "text"
                    metadata["content"] = text
                    vector = self.embedding_handler.get_text_embedding_offline(text)
                    text_vectors.append(vector)
                    metadata_store.append(metadata)
                    doc_id_counter += 1

        # Recursively get all image files
        img_files = get_all_files_in_directory(img_dir, ['.png', '.jpg', '.jpeg', '.bmp', '.gif'])
        print(f"Found {len(img_files)} image files")

        # Image vectorization
        for img_path in img_files:
            img_filename = os.path.basename(img_path)
            relative_img_path = os.path.relpath(img_path, start=img_dir)
            ocr_text = self.embedding_handler.image_to_text(img_path)
            metadata = {"id": doc_id_counter, "source": f"Image: {relative_img_path}",
                        "type": "image", "path": img_path, "ocr": ocr_text, "page": 1}
            vector = self.embedding_handler.get_image_embedding_mps(img_path)
            image_vectors.append(vector)
            metadata_store.append(metadata)
            doc_id_counter += 1

        # Build FAISS index
        text_index = faiss.IndexFlatIP(self.TEXT_EMBEDDING_DIM)
        text_index_map = faiss.IndexIDMap(text_index)
        if text_vectors:
            text_ids = [m["id"] for m in metadata_store if m["type"]=="text"]
            text_index_map.add_with_ids(np.array(text_vectors), np.array(text_ids))
            faiss.write_index(text_index_map, TEXT_FAISS_FILE)

        image_index = faiss.IndexFlatIP(IMAGE_EMBEDDING_DIM)
        image_index_map = faiss.IndexIDMap(image_index)
        if image_vectors:
            image_ids = [m["id"] for m in metadata_store if m["type"]=="image"]
            image_index_map.add_with_ids(np.array(image_vectors), np.array(image_ids))
            faiss.write_index(image_index_map, IMAGE_FAISS_FILE)

        # Save metadata_store
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata_store, f, ensure_ascii=False, indent=2)

        print(f"Initial knowledge base building completed: {len(text_vectors)} text, {len(image_vectors)} images")
        return metadata_store, text_index_map, image_index_map

    def add_documents_to_knowledge_base(self, docs_dir=DOCS_DIR, img_dir=IMG_DIR):
        """
        Incrementally add documents to existing knowledge base
        """
        print("\n--- Incrementally Adding Documents to Knowledge Base ---")
        
        # First check if existing knowledge base exists
        if not (os.path.exists(TEXT_FAISS_FILE) and os.path.exists(IMAGE_FAISS_FILE) and os.path.exists(METADATA_FILE)):
            print("No existing knowledge base detected, building initial knowledge base...")
            return self.build_initial_knowledge_base(docs_dir, img_dir)
        
        # Load existing knowledge base
        metadata_store, text_index_map, image_index_map = self.load_existing_knowledge_base()
        
        # Determine next document ID
        next_doc_id = max([item["id"] for item in metadata_store], default=-1) + 1
        
        # Count newly added vectors
        initial_text_count = text_index_map.ntotal
        initial_image_count = image_index_map.ntotal

        # Get existing document paths to avoid duplicate processing
        existing_doc_paths = {item["source"] for item in metadata_store if item["type"] == "text"}
        existing_img_paths = {item["path"] for item in metadata_store if item["type"] == "image"}

        # Recursively get all document files
        doc_files = get_all_files_in_directory(docs_dir, ['.docx', '.pdf', '.txt'])
        print(f"Found {len(doc_files)} document files")

        # Document vectorization (incremental addition)
        for file_path in doc_files:
            relative_path = os.path.relpath(file_path, start=docs_dir)
            
            # Check if document already exists
            if relative_path in existing_doc_paths:
                print(f"Document already exists, skipping: {file_path}")
                continue
                
            filename = os.path.basename(file_path)
            print(f"Processing new document: {file_path}")
            chunks = parse_document(file_path)
            for chunk in chunks:
                metadata = {"id": next_doc_id, "source": relative_path, "page": 1}
                if chunk["type"] in ["text", "table"]:
                    text = chunk["content"]
                    if not text.strip():
                        continue
                    metadata["type"] = "text"
                    metadata["content"] = text
                    vector = self.embedding_handler.get_text_embedding_offline(text)
                    
                    # Add to text index
                    text_index_map.add_with_ids(np.array([vector]), np.array([next_doc_id]))
                    
                    metadata_store.append(metadata)
                    next_doc_id += 1

        # Recursively get all image files
        img_files = get_all_files_in_directory(img_dir, ['.png', '.jpg', '.jpeg', '.bmp', '.gif'])
        print(f"Found {len(img_files)} image files")

        # Image vectorization (incremental addition)
        for img_path in img_files:
            relative_img_path = os.path.relpath(img_path, start=img_dir)
            
            # Check if image already exists (based on full path)
            if img_path in existing_img_paths:
                print(f"Image already exists, skipping: {img_path}")
                continue
            
            ocr_text = self.embedding_handler.image_to_text(img_path)
            metadata = {"id": next_doc_id, "source": f"Image: {relative_img_path}",
                        "type": "image", "path": img_path, "ocr": ocr_text, "page": 1}
            vector = self.embedding_handler.get_image_embedding_mps(img_path)
            
            # Add to image index
            image_index_map.add_with_ids(np.array([vector]), np.array([next_doc_id]))
            
            metadata_store.append(metadata)
            next_doc_id += 1

        # Save updated index and metadata
        faiss.write_index(text_index_map, TEXT_FAISS_FILE)
        faiss.write_index(image_index_map, IMAGE_FAISS_FILE)
        
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata_store, f, ensure_ascii=False, indent=2)

        # Count newly added items
        new_text_count = text_index_map.ntotal - initial_text_count
        new_image_count = image_index_map.ntotal - initial_image_count
        
        print(f"Knowledge base incremental update completed: Added {new_text_count} text, {new_image_count} images")
        return metadata_store, text_index_map, image_index_map

    def build_or_load_knowledge_base(self, docs_dir=DOCS_DIR, img_dir=IMG_DIR):
        """
        Build or load knowledge base
        """
        print("\n--- Building/Loading Knowledge Base ---")
        
        # Try to load existing FAISS index and metadata_store
        if os.path.exists(TEXT_FAISS_FILE) and os.path.exists(IMAGE_FAISS_FILE) and os.path.exists(METADATA_FILE):
            print("Existing knowledge base detected, loading...")
            return self.load_existing_knowledge_base()
        else:
            print("No existing knowledge base detected, starting build...")
            return self.build_initial_knowledge_base(docs_dir, img_dir)