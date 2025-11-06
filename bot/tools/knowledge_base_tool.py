import json
from typing import Dict, Any
from qwen_agent.tools.base import BaseTool
import dotenv

from ..core.ollama_handler import generate_local_answer
from ..config import SYSTEM_ROLE

dotenv.load_dotenv()
        
class RAGTool(BaseTool):
    """
    RAG tool for retrieving information from the knowledge base and generating an answer.
    """
    name = 'search_knowledge_base'
    description = 'Search the knowledge base for information about the theme park and use it to answer the user\'s question.'
    parameters = [
        {"name": "query", "type": "string", "description": "The user\'s question to search for in the knowledge base"},
        {"name": "k", "type": "integer", "description": "Number of results to return", "required": False}
    ]

    def __init__(self, rag_engine, metadata_store, text_index, image_index):
        self.rag_engine = rag_engine
        self.metadata_store = metadata_store
        self.text_index = text_index
        self.image_index = image_index

    def call(self, query: str, k: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Search the knowledge base, then use an LLM to generate a final answer.
        """
        try:
            # --- Step 1: Retrieve documents ---
            retrieved_context = []
            query_vec = self.rag_engine.embedding_handler.get_text_embedding_offline(query).reshape(1, -1)
            
            distances, ids = self.text_index.search(query_vec, k)
            
            for doc_id in ids[0]:
                if doc_id != -1:
                    match = next((item for item in self.metadata_store if item["id"] == doc_id), None)
                    if match:
                        retrieved_context.append({
                            "id": match["id"],
                            "content": match.get("content", ""),
                            "source": match.get("source", "Unknown"),
                            "type": match.get("type", "text")
                        })
            
            if any(keyword in query.lower() for keyword in ["poster", "image", "picture", "activity", "what does it look like"]):
                query_vec_img = self.rag_engine.embedding_handler.get_clip_text_embedding_cpu(query).reshape(1, -1)
                distances, image_ids = self.image_index.search(query_vec_img, 1)
                
                for doc_id in image_ids[0]:
                    if doc_id != -1:
                        match = next((item for item in self.metadata_store if item["id"] == doc_id), None)
                        if match:
                            retrieved_context.append({
                                "id": match["id"],
                                "content": f"Related image path: {match['path']}, Image text: '{match['ocr']}'",
                                "source": match.get("source", "Unknown"),
                                "type": "image",
                                "path": match.get("path") # Ensure path is included
                            })

            if not retrieved_context:
                return {
                    "success": True,
                    "answer": "I couldn't find any relevant information in the knowledge base to answer your question.",
                    "results": []
                }

            # --- Step 2: Augment prompt with context ---
            context_str = ""
            for i, item in enumerate(retrieved_context):
                content = item.get('content','')
                source = item.get('source','Unknown Source')
                context_str += f"Background Knowledge {i+1} (Source: {source}):\n{content}\n\n"
            
            prompt = f"""{SYSTEM_ROLE}. Please answer the user's question using a friendly and professional tone based on the following background knowledge. Please only use information from the background knowledge, do not make up information.

                        [Background Knowledge]
                        {context_str}
                        [User Question]
                        {query}
                        """
            # --- Step 3: Generate answer with Ollama ---
            final_answer = generate_local_answer(prompt)

            image_path_found = None
            for item in retrieved_context:
                if item.get("type") == "image":
                    image_path_found = item.get("path")
                    break
            if image_path_found:
                final_answer += f"\n\n(Found related image: {image_path_found})"

            # --- Step 4: Return the final answer and sources ---
            output = {
                "success": True,
                "answer": final_answer,
                "results": retrieved_context
            }
            return json.dumps(output, ensure_ascii=False)

        except Exception as e:
            import traceback
            print(f"Error in RAGTool: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Error in RAG tool: {str(e)}"
            }
