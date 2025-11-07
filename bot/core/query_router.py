"""
Query Router for the intelligent assistant using Qwen Agent
"""
import json
import os
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

from ..core.ollama_handler import generate_local_answer

from ..tools.weather_tool import WeatherTool
from ..tools.sql_tool import SQLTool
from ..tools.knowledge_base_tool import RAGTool
from ..config import SYSTEM_ROLE

load_dotenv()

class QueryRouter:
    """
    Intelligent query router using Qwen Assistant for tool selection.
    """
    def __init__(self, rag_engine, metadata_store, text_index, image_index):
        # First, instantiate the tools with their dependencies
        sql_tool_instance = SQLTool()
        weather_tool_instance = WeatherTool()
        rag_tool_instance = RAGTool(rag_engine, metadata_store, text_index, image_index)
        map_tool = {
            "mcpServers": {
                "google-maps": {
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-google-maps"
                ],
                "command": "npx",
                "env": {
                    "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY", "")
                }
                }
            }
            }

        # Configure the LLM for the agent
        self.llm_cfg = {
            'model': 'qwen-turbo',
            'api_key': os.getenv('DASHSCOPE_API_KEY', ''),
            'temperature': 0.2,
            'timeout': 30,
            'retry_count': 3,
        }
        
        # Initialize Qwen Assistant with the tool instances
        self.assistant = Assistant(
            llm=self.llm_cfg,
            name='Intelligent Assistant of a Theme Park',
            description='Intelligent assistant that can query weather, database, and knowledge base',
            system_message=f"""{SYSTEM_ROLE}. Use tools to answer queries.

            Tools:
            - {weather_tool_instance.name}: {weather_tool_instance.description}
            - {sql_tool_instance.name}: {sql_tool_instance.description}
            - {rag_tool_instance.name}: {rag_tool_instance.description}
            - google-maps: Plan routes and get location-based information using Google Maps API.

            CRITICAL RULES:
            - You MUST call a tool function for every user query.
            - NEVER answer directly without calling a tool.
            - Parameters MUST be provided in valid JSON format.
            - Extract parameter values from the user's question.
            - If unsure which tool to use, default to search_knowledge_base.
            """,
            function_list=[weather_tool_instance, sql_tool_instance, rag_tool_instance, map_tool],
        )

    def route_query(self, query: str) -> dict:
        """
        Send the query to the assistant, which will execute the appropriate tool.
        """
        try:
            messages = [{'role': 'user', 'content': query}]
            # The agent will run and call the appropriate tool's `call` method
            for response in self.assistant.run(messages):
                # The final response from the agent will contain the tool's output
                if response and len(response) > 0:
                    last_message = response[-1]
                    # The tool's output is in the 'content' of the 'function' role message
                    if last_message.get('role') == 'function':
                        tool_name = last_message.get("name", "")
                        content = last_message.get("content", "")

                        #if map_tool is used, parse the response
                        if "maps" in tool_name.lower():
                            parsed_answer = _parse_maps_response(content)
                            return {
                                "success": True,
                                "tool": tool_name,
                                "result": parsed_answer
                            }

                        return {
                            "success": True,
                            "tool": tool_name,
                            "result": content
                        }

            # Fallback if no tool was called
            return {"success": False, "tool": "unknown", "error": "Assistant did not call a tool."}

        except Exception as e:
            import traceback
            print(f"❌ Router error traceback:\n{traceback.format_exc()}")
            return {"success": False, "tool": "unknown", "error": f"Error routing query: {repr(e)}"}
        
def _parse_maps_response(content: any):
    # Extract relevant information from the maps API response
    prompt = f"""
            You are an expert assistant for parsing Google Maps API responses. 
            Convert the following content into a concise, user-friendly natural language description.
            Answer in the same language as the user query.
            Response:
            {content}
            Answer:
            """
    answer = generate_local_answer(prompt)
    return answer