"""
Query Router for the intelligent assistant using Qwen Agent
"""
import json
import os
from typing import Dict, Any
from qwen_agent.agents import Assistant
from dotenv import load_dotenv
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import register_tool

from ..tools.weather_tool import WeatherTool
from ..tools.sql_tool import SQLTool
from ..tools.knowledge_base_tool import RAGTool
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

        register_tool("get_weather")(WeatherTool)
        register_tool('execute_sql_query')(SQLTool)
        register_tool('search_knowledge_base')(RAGTool)
        
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
            system_message = f"""
                {SYSTEM_ROLE}. You answer user queries by selecting and calling the proper tools.
                Rules:
                1. ALWAYS call a function from the function_list.
                2. DO NOT answer directly!
                3. If not sure which function to call, call `search_knowledge_base`.
                4. Provide arguments in JSON format.

                Function list (available tools):
                1. get_weather
                Description: Query the weather for a specific location and date
                Arguments: {{"location": "city name"}}

                2. execute_sql_query
                Description: Convert natural language query to SQL and execute it on the database
                Arguments: {{"query": "<user's original question>"}}

                3. search_knowledge_base
                Description: Retrieve tips, recommendations, etc. from vector database
                Arguments: {{"query": "<user's original question>"}}
                """,

            function_list=['get_weather', 'execute_sql_query', 'search_knowledge_base'],
        )

    def route_query(self, query: str) -> dict:
        """
        Send the query to the assistant, determine which tool was called,
        and return a simplified response with success, tool, and answer.
        """
        try:
            messages = [{'role': 'user', 'content': query}]

            for response in self.assistant.run(messages):
                if response and len(response) > 0:
                    last_response = response[-1]

                    function_call = last_response.get("function_call")
                    content = last_response.get("content", "")

                    if function_call and "name" in function_call:
                        return {
                            "success": True,
                            "tool": function_call["name"],
                            "answer": content.strip() if content else None
                        }

                    if content:
                        return {
                            "success": True,
                            "tool": "search_knowledge_base",
                            "answer": content.strip()
                        }

                    # fallback if no content or function_call
                    return {
                        "success": True,
                        "tool": "search_knowledge_base",
                        "answer": "No content returned from assistant."
                    }

            # If assistant.run returns nothing
            return {"success": False, "tool": "unknown", "answer": None}

        except Exception as e:
            return {"success": False, "tool": "unknown", "answer": f"Error routing query: {str(e)}"}


