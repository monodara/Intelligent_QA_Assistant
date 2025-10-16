"""
Usage example: How to add new documents to knowledge base (supports nested directories)
"""
from bot.knowledge_base import KnowledgeBaseManager
from bot.config import DOCS_DIR, IMG_DIR


def add_new_documents_to_knowledge_base(new_docs_dir, new_img_dir=None):
    """
    Function to incrementally add new documents to existing knowledge base (supports nested directories)
    """
    kb_manager = KnowledgeBaseManager()
    
    # If only adding new documents, you can specify new document directory
    if new_img_dir is None:
        new_img_dir = IMG_DIR  # Use default image directory
    
    print(f"Adding new documents to knowledge base incrementally:")
    print(f"  New document directory: {new_docs_dir}")
    print(f"  New image directory: {new_img_dir}")
    print("  (System will automatically recursively scan all subdirectories)")
    
    # Incrementally add to existing knowledge base, automatically handle nested directories
    metadata_store, text_index, image_index = kb_manager.add_documents_to_knowledge_base(
        docs_dir=new_docs_dir,
        img_dir=new_img_dir
    )
    
    print("New documents (including documents in nested directories) have been successfully added to existing knowledge base!")
    return metadata_store, text_index, image_index


def rebuild_knowledge_base_from_scratch(docs_dir=DOCS_DIR, img_dir=IMG_DIR):
    """
    Function to rebuild entire knowledge base from scratch (supports nested directories)
    """
    kb_manager = KnowledgeBaseManager()
    
    print(f"Rebuilding entire knowledge base...")
    print(f"Document directory: {docs_dir}")
    print(f"Image directory: {img_dir}")
    print("(System will automatically recursively scan all subdirectories)")
    
    # Rebuild entire knowledge base, automatically handle nested directories
    metadata_store, text_index, image_index = kb_manager.build_initial_knowledge_base(
        docs_dir=docs_dir,
        img_dir=img_dir
    )
    
    print("Knowledge base (including documents in nested directories) has been completely rebuilt!")
    return metadata_store, text_index, image_index


# Usage example
if __name__ == "__main__":
    print("Knowledge base management usage examples:")
    print("1. Incrementally add new documents (supports nested directories):")
    print("   add_new_documents_to_knowledge_base('new_documents_with_nested_dirs')")
    print("2. Completely rebuild knowledge base (supports nested directories):")
    print("   rebuild_knowledge_base_from_scratch('documents_with_nested_dirs')")
    
    # Example: Add new documents in nested directories to existing knowledge base
    # add_new_documents_to_knowledge_base("new_documents_with_nested_dirs", "new_images_with_nested_dirs")
    
    print("\nNote: System will automatically recursively scan document files in specified directory and all its subdirectories.")