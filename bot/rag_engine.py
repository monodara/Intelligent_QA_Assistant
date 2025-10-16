from .config import DEFAULT_RETRIEVAL_K
from .embedding_handler import EmbeddingHandler
from .ollama_handler import generate_local_answer


class RAGEngine:
    def __init__(self):
        self.embedding_handler = EmbeddingHandler()

    def rag_ask(self, metadata_store, text_index, image_index, k=DEFAULT_RETRIEVAL_K):
        """
        Execute RAG Q&A process
        :param metadata_store: Metadata storage
        :param text_index: Text FAISS index
        :param image_index: Image FAISS index
        :param k: Number of documents to retrieve
        """
        query = input("Please enter your question: ").strip()
        if not query:
            print("Question is empty, exiting")
            return

        retrieved_context = []

        # Text retrieval
        query_vec = self.embedding_handler.get_text_embedding_offline(query).reshape(1,-1)
        distances, ids = text_index.search(query_vec, k)
        for doc_id in ids[0]:
            if doc_id != -1:
                match = next((item for item in metadata_store if item["id"]==doc_id), None)
                if match:
                    retrieved_context.append(match)
                    print(f"  - Text hit ID:{doc_id}")

        # Image retrieval
        if any(keyword in query.lower() for keyword in ["poster","图片","看看","活动","长什么样"]):
            query_vec_img = self.embedding_handler.get_clip_text_embedding_cpu(query).reshape(1,-1)
            print(f"Image retrieval vector dimension: {query_vec_img.shape}")
            distances, image_ids = image_index.search(query_vec_img, 1)
            for doc_id in image_ids[0]:
                if doc_id != -1:
                    match = next((item for item in metadata_store if item["id"]==doc_id), None)
                    context_text = f"Related image path: {match['path']}, Image text: '{match['ocr']}'"
                    retrieved_context.append({"type":"image_context","content":context_text,"metadata":match})
                    print(f"  - Image hit ID:{doc_id}")

        # Build Prompt
        context_str = ""
        for i, item in enumerate(retrieved_context):
            content = item.get('content','')
            source = item.get('metadata',{}).get('source', item.get('source','Unknown Source'))
            context_str += f"Background Knowledge {i+1} (Source: {source}):\n{content}\n\n"

        from .config import SYSTEM_ROLE
        
        prompt = f"""{SYSTEM_ROLE}. Please answer the user's question using a friendly and professional tone based on the following background knowledge. Please only use information from the background knowledge, do not make up information.

[Background Knowledge]
{context_str}
[User Question]
{query}
"""
        print("--- Prompt ---")
        print(prompt)
        print("--- Prompt End ---\n")

        final_answer = generate_local_answer(prompt)

        # Image prompt
        image_path_found = None
        for item in retrieved_context:
            if item.get("type")=="image_context":
                image_path_found = item.get("metadata",{}).get("path")
                break
        if image_path_found:
            final_answer += f"\n\n(Found related image: {image_path_found})"

        print("--- Final Answer ---")
        print(final_answer)