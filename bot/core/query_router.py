"""
Query Router for the intelligent assistant using Qwen Assistant
Implements tool selection using Qwen Assistant agent similar to assistant_weather_bot-1.py
"""
import json
import os
from typing import Dict, Any
from qwen_agent.agents import Assistant
from dotenv import load_dotenv
# Removed direct imports of WeatherTool, RAGTool, SQLTool as they are managed by Qwen Agent
from ..config import SYSTEM_ROLE

load_dotenv()

class QueryRouter:
    """
    Intelligent query router using Qwen Assistant for tool selection
    Based on the Assistant pattern from assistant_weather_bot-1.py
    """
    def __init__(self, rag_engine, metadata_store, text_index, image_index):
        self.rag_engine = rag_engine
        self.metadata_store = metadata_store
        self.text_index = text_index
        self.image_index = image_index
        
        # Configure LLM
        self.llm_cfg = {
            'model': os.getenv('QWEN_MODEL', 'qwen-turbo'),  # Use environment variable or default
            'api_key': os.getenv('DASHSCOPE_API_KEY', ''),
            'temperature': 0.2,
            'timeout': 30,
            'retry_count': 3,
        }
        
        # Initialize Qwen Assistant with the three tools
        self.assistant = Assistant(
            llm=self.llm_cfg,
            name='Intelligent Assistant of a Theme Park',
            description='Intelligent assistant that can query weather, database, and knowledge base',
            system_message=f"{SYSTEM_ROLE}. Always call a function from function_list when the user query requires external info. "
                           f"Always provide arguments in JSON format. DO NOT answer directly unless you cannot call any function."
                           "1. get_weather: Query the weather conditions for a specified location at a specific date. Required argument: {{ \"location\": \"city name\" }}\n"
                           "2. execute_sql_query: Query ticket prices/visitor flow(based on used tickets)\n"
                           "3. search_knowledge_base: Retrieve travel tips and recommendations",
            function_list=['get_weather', 'execute_sql_query', 'search_knowledge_base'],
        )

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Route the query using Qwen Assistant to determine which tool to call
        """
        try:
            # Prepare messages for the assistant
            messages = [
                {
                    'role': 'user',
                    'content': query
                }
            ]
            
            final_content = ""
            # Run the assistant to get tool selection and execution
            for response in self.assistant.run(messages):
                print("Assistant response:", response)
                if response and len(response) > 0:
                    last_response = response[-1]  # Get the final response
                    final_content = last_response.get('content', '')
                    # If a response is received, process it and break
                    return self._process_assistant_response(final_content, query)
            
            # If the loop finishes without returning (i.e., no response from assistant)
            if not final_content:
                return {
                    "success": False,
                    "tool": "unknown",
                    "error": "No response from assistant and no tool selected."
                }
            
            # Fallback if for some reason the loop completes but final_content has something
            return self._process_assistant_response(final_content, query)
            
        except Exception as e:
            # If assistant fails, return error
            return {
                "success": False,
                "tool": "unknown",
                "error": f"Error making routing decision with Qwen Assistant: {str(e)}"
            }

    def _process_assistant_response(self, content: str, original_query: str) -> Dict[str, Any]:
        """
        Process the content from Qwen Assistant, which is either a tool's result or a direct LLM answer.
        """
        try:
            # Attempt to parse content as JSON, indicating a tool result
            tool_result = json.loads(content)

            # Check for specific tool result patterns
            # WeatherTool returns a dict like {"success": True, "source": "forecast", ...}
            if "location" in tool_result and "date" in tool_result and ("weather" in tool_result or "avg_temp" in tool_result):
                return {
                    "success": tool_result.get("success", False),
                    "tool": "get_weather",
                    "query": original_query,
                    "weather_data": tool_result
                }
            # SQLTool returns a dict like {"success": True, "sql": "...", "answer": "...", "data": [...]}
            elif "sql" in tool_result and "answer" in tool_result and "data" in tool_result:
                return {
                    "success": tool_result.get("success", False),
                    "tool": "execute_sql_query",
                    "query": original_query,
                    "answer": tool_result.get("answer"),
                    "data": tool_result.get("data")
                }
            # RAGTool returns a dict like {"success": True, "results": [...], "count": ...}
            elif "results" in tool_result and "count" in tool_result:
                return {
                    "success": tool_result.get("success", False),
                    "tool": "search_knowledge_base",
                    "query": original_query,
                    "knowledge_base_results": tool_result.get("results"),
                    "result_count": tool_result.get("count")
                }
            else:
                # If it's JSON but doesn't match known tool result patterns, treat as direct LLM answer
                return {
                    "success": True,
                    "tool": "LLM_direct_answer",
                    "query": original_query,
                    "answer": content # Original content as the answer
                }

        except json.JSONDecodeError:
            # If content is not JSON, it's a direct LLM answer
            return {
                "success": True,
                "tool": "LLM_direct_answer",
                "query": original_query,
                "answer": content
            }
        except Exception as e:
            return {
                "success": False,
                "tool": "unknown",
                "query": original_query,
                "error": f"Error processing assistant response: {str(e)}"
            }
