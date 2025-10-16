from .knowledge_base import KnowledgeBaseManager
from .rag_engine import RAGEngine
from .config import DOCS_DIR, IMG_DIR


def main():
    # Initialize knowledge base
    kb_manager = KnowledgeBaseManager()
    metadata_store, text_index, image_index = kb_manager.build_or_load_knowledge_base(DOCS_DIR, IMG_DIR)
    
    print("\n=============================================")
    print("Local Multimodal RAG Assistant Ready")
    print("=============================================")

    # Initialize RAG engine
    rag_engine = RAGEngine()

    # Run Q&A loop
    while True:
        rag_engine.rag_ask(metadata_store, text_index, image_index)


if __name__ == "__main__":
    main()