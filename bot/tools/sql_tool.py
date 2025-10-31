"""
SQL Tool for querying PostgreSQL database
Used for querying tickets/visitor flow/historical data
"""
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

import dashscope
from dashscope import Generation
import pandas as pd
from sqlalchemy import create_engine
from qwen_agent.tools.base import BaseTool, register_tool

load_dotenv()

@register_tool('execute_sql_query')
class SQLTool(BaseTool):
    """
    SQL Tool for communicating with PostgreSQL database
    """
    description = 'Convert natural language to SQL, execute it, and analyze the results.'

    def __init__(self, cfg=None):
        # Use environment variable or default connection string
        self.engine = create_engine(os.getenv('POSTGRES_CONNECTION_STRING'))

        self.llm_cfg = {
            "model": os.getenv("QWEN_MODEL", "qwen-turbo"),
            "api_key": os.getenv("DASHSCOPE_API_KEY", ""),
            "temperature": 0.1,
            "timeout": 30
        }
    
    def call(self, params: str) -> str:
        """
        Qwen Agent call interface
        params: JSON {"query": "Natural language query"}
        """
        args = json.loads(params)
        query = args.get("query", "")
        
        # Step 1: Use LLM to convert natural language to SQL
        sql = self.nl_to_sql(query)
        if not sql:
            return json.dumps({"success": False, "error": "Unable to generate SQL"}, ensure_ascii=False)
        
        # Step 2: Execute SQL
        sql_result = self.execute_sql(sql)
        if not sql_result["success"]:
            return json.dumps(sql_result, ensure_ascii=False)
        
        # Step 3: Analyse results based on original query
        answer = self.analyze_results(sql_result["results"], query)
        return json.dumps({"success": True, "sql": sql, "answer": answer, "data": sql_result["results"]}, ensure_ascii=False)

    def nl_to_sql(self, query: str) -> str:
        """
        Convert natural language to SQL
        """
        create_sql = """
-- Table: visit_flow
-- Columns:
    visit_date DATE NOT NULL,                     -- Visit date (core field for daily aggregation)
    entry_time TIMESTAMP WITH TIME ZONE,          -- Entry time (precise to seconds)
    exit_time TIMESTAMP WITH TIME ZONE,           -- Exit time
"""


        prompt = f"""-- language: SQL
### Question: {query}
### Table schema:
{create_sql}
### Response:
Write an SQL query that answers the question: `{query}`
```sql
"""


        # Call Qwen LLM to generate SQL
        dashscope.api_key = self.llm_cfg["api_key"]
        response =Generation.call(
            model=self.llm_cfg["model"],
            prompt=prompt,
            temperature=self.llm_cfg["temperature"],
            max_tokens=300
        )

        # Extract SQL from response
        sql_text = getattr(response, "output", None)

        # 如果不是字符串，转换为字符串
        if not isinstance(sql_text, str):
            sql_text = str(sql_text)

        # 去掉 ```sql 开头和 ``` 结尾
        sql_text = sql_text.strip()
        if sql_text.startswith("```sql"):
            sql_text = sql_text[6:].strip()
        if sql_text.endswith("```"):
            sql_text = sql_text[:-3].strip()

        return sql_text or ""

    def execute_sql(self, sql: str) -> dict:
        try:
            df = pd.read_sql(sql, self.engine)
            return {"success": True, "results": df.to_dict(orient="records"), "count": len(df)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_results(self, results: list, original_query: str) -> str:
        """
        Use LLM to generate a natural language answer based on SQL query results
        and the original user question.
        """

        if not results:
            return "No data found for your query."

        preview_results = results[:10]  # Temporarily limit to first 10 records
        results_str = json.dumps(preview_results, ensure_ascii=False)

        prompt = f"""
    You are a professional data analysis assistant. Please help to answer the user's question based on the SQL query results provided.
    User asked: "{original_query}"
    The database query returned the following results (first 10 rows):
    {results_str}

    Please provide a clear, concise answer to the user's question based on the data above.
    """
        # Call Qwen LLM
        dashscope.api_key = self.llm_cfg["api_key"]
        response = Generation.call(
            model=self.llm_cfg["model"],
            prompt=prompt,
            temperature=0.2,
            max_tokens=300
        )
        print("LLM 响应:", response.output)
        answer = getattr(response, "output", None)

        # If the response is not a string, convert it to string
        if not isinstance(answer, str):
            answer = str(answer)

        # Remove code block markers if present
        answer = answer.strip()
        if answer.startswith("```"):
            answer = answer[3:].strip()
        if answer.endswith("```"):
            answer = answer[:-3].strip()

        return answer
