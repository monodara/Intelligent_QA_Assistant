from typing import Dict, Any
from qwen_agent.tools.base import BaseTool, register_tool
import dotenv

dotenv.load_dotenv()
        
@register_tool('search_knowledge_base')       
class RAGTool(BaseTool):
    """
    RAG tool for retrieving information from knowledge base
    This is a wrapper around the existing RAG functionality
    """
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
    
    def call(self, query: str, metadata_store, text_index, image_index, k: int = 5) -> Dict[str, Any]:
        """
        Search the knowledge base for relevant information
        """
        try:
            # Use the embedding handler to convert query to vector
            query_vec = self.rag_engine.embedding_handler.get_text_embedding_offline(query).reshape(1, -1)
            
            # Search in text index
            distances, ids = text_index.search(query_vec, k)
            results = []
            
            for doc_id in ids[0]:
                if doc_id != -1:
                    match = next((item for item in metadata_store if item["id"] == doc_id), None)
                    if match:
                        results.append({
                            "id": match["id"],
                            "content": match.get("content", ""),
                            "source": match.get("source", "Unknown"),
                            "type": match.get("type", "text")
                        })
            
            # Also search in image index if relevant
            if any(keyword in query.lower() for keyword in ["poster", "图片", "看看", "活动", "长什么样"]):
                query_vec_img = self.rag_engine.embedding_handler.get_clip_text_embedding_cpu(query).reshape(1, -1)
                distances, image_ids = image_index.search(query_vec_img, 1)
                
                for doc_id in image_ids[0]:
                    if doc_id != -1:
                        match = next((item for item in metadata_store if item["id"] == doc_id), None)
                        if match:
                            results.append({
                                "id": match["id"],
                                "content": f"Related image path: {match['path']}, Image text: '{match['ocr']}'",
                                "source": match.get("source", "Unknown"),
                                "type": "image"
                            })
            
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching knowledge base: {str(e)}"
            }