"""
Knowledge Base Building Script
Used to run separately to build or incrementally update knowledge base
"""
import os
import sys
from ..core.knowledge_base import KnowledgeBaseManager
from ..config import DOCS_DIR, IMG_DIR


def build_or_update_knowledge_base(docs_dir=DOCS_DIR, img_dir=IMG_DIR, incremental=True):
    """
    Standalone function to build or incrementally update knowledge base
    """
    kb_manager = KnowledgeBaseManager()
    
    if incremental:
        # Incrementally add to existing knowledge base
        metadata_store, text_index, image_index = kb_manager.add_documents_to_knowledge_base(docs_dir, img_dir)
    else:
        # Rebuild entire knowledge base
        metadata_store, text_index, image_index = kb_manager.build_initial_knowledge_base(docs_dir, img_dir)
    
    print(f"Knowledge base {'incremental update' if incremental else 'building'} completed! Contains {len(metadata_store)} document chunks.")
    return metadata_store, text_index, image_index


def main(docs_dir=DOCS_DIR, img_dir=IMG_DIR, incremental=True):
    """
    Main function for command line invocation
    """
    print(f"Starting {'incremental update' if incremental else 'building'} knowledge base...")
    print(f"Document directory: {docs_dir}")
    print(f"Image directory: {img_dir}")
    print(f"Incremental mode: {incremental}")
    
    try:
        build_or_update_knowledge_base(docs_dir, img_dir, incremental)
        print("Knowledge base building/update completed!")
    except Exception as e:
        print(f"Knowledge base building/update failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Get document and image directories from command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Knowledge base building/update script")
    parser.add_argument("--docs-dir", default=DOCS_DIR, help="Document directory path")
    parser.add_argument("--img-dir", default=IMG_DIR, help="Image directory path")
    parser.add_argument("--incremental", action="store_true", default=True, help="Whether to use incremental mode (default is True)")
    parser.add_argument("--full-rebuild", action="store_true", default=False, help="Full rebuild mode (default is False)")
    
    args = parser.parse_args()
    
    incremental = args.incremental and not args.full_rebuild
    
    main(docs_dir=args.docs_dir, img_dir=args.img_dir, incremental=incremental)