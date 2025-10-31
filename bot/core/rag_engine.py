from .embedding_handler import EmbeddingHandler


class RAGEngine:
    """
    A wrapper for core embedding models and handlers.
    The main retrieval logic is in RAGTool.
    This engine's primary role is to provide the embedding handler to other components.
    """
    def __init__(self):
        self.embedding_handler = EmbeddingHandler()
