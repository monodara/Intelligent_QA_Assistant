"""
SQL Tool for querying PostgreSQL database
Used for querying tickets/visitor flow/historical data
"""
import os
import json
import re
from typing import Dict, Any
from dotenv import load_dotenv

import dashscope
from dashscope import Generation
import pandas as pd
from sqlalchemy import create_engine
from qwen_agent.tools.base import BaseTool, register_tool

from ..core.ollama_handler import generate_local_answer

load_dotenv()

class SQLTool(BaseTool):
    """
    SQL Tool for communicating with PostgreSQL database
    """
    name = "text_to_sql"
    description = 'Convert natural language to SQL, execute it, and analyze the results.'
    parameters = [
        {"name": "query", "type": "string", "description": "Natural language query"}
    ]

    def __init__(self, cfg=None):
        # Use environment variable or default connection string
        self.engine = create_engine(os.getenv('POSTGRES_CONNECTION_STRING'))

        self.llm_cfg = {
            "model": "qwen-turbo",
            "api_key": os.getenv("DASHSCOPE_API_KEY", ""),
            "temperature": 0.1,
            "timeout": 30
        }
    
    def call(self, params: str, **kwargs) -> str:
        """
        Qwen Agent call interface
        params: JSON {"query": "Natural language query"}
        """
        if isinstance(params, str):
            try:
                params_dict = json.loads(params)
                query_text = params_dict.get("query", params)
            except json.JSONDecodeError:
                query_text = params
        elif isinstance(params, dict):
            query_text = params.get("query") or params.get("text") or ""
        else:
            query_text = ""

        if not query_text.strip():
            return json.dumps({"success": False, "error": "No SQL query text provided."}, ensure_ascii=False)
        
        # Step 1: Use LLM to convert natural language to SQL
        sql = self.nl_to_sql(query_text)
        if not sql:
            return json.dumps({"success": False, "error": "Unable to generate SQL"}, ensure_ascii=False)
        
        # Step 2: Execute SQL
        sql_result = self.execute_sql(sql)
        if not sql_result["success"]:
            return json.dumps(sql_result, ensure_ascii=False)
        
        # Step 3: Analyse results based on original query
        answer_str = self.analyze_results(sql_result["results"], query_text)

        # Step 4: Construct the final dictionary and return as a JSON string
        output = {
            "success": True,
            "sql": sql,
            "answer": answer_str,
            "data": sql_result["results"]
        }
        return json.dumps(output, ensure_ascii=False)

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

        sql_text = getattr(response, "output", None)

        # 如果不是字符串，先转为字符串
        if not isinstance(sql_text, str):
            sql_text = str(sql_text)

        # 1️⃣ 尝试从 JSON 中提取 "text" 字段
        try:
            data = json.loads(sql_text)
            if "text" in data:
                sql_text = data["text"]
        except Exception:
            # 如果解析失败，就直接用原始字符串
            pass

        # 2️⃣ 用正则提取 ```sql ... ``` 中间的部分（去掉解释内容）
        match = re.search(r"```sql\s*(.*?)\s*```", sql_text, re.DOTALL)
        if match:
            sql_text = match.group(1).strip()

        # 3️⃣ 再清理残余的 Markdown 标记
        sql_text = sql_text.replace("```", "").strip()

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
                You are an expert data analyst assistant. Answer the user's question based on the SQL query results.

                User question: "{original_query}"

                The SQL query returned the following results (first 10 rows or aggregation results):
                {results_str}

                Instructions:
                1. The results may include aggregated or summary data (e.g., MAX, COUNT, etc.).
                2. Even if the SQL result has only one row, provide a complete, concise natural language answer to the user's question.
                3. Focus only on the information in the SQL results.
                4. Keep the answer clear and precise, suitable for end-user understanding.

                Answer:
                """
        answer = generate_local_answer(prompt)
        return answer