"""
SQL Tool for querying PostgreSQL database
Used for querying tickets/visitor flow/historical data
"""
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

import dashscope
import pandas as pd
from sqlalchemy import create_engine
from qwen_agent.tools.base import BaseTool, register_tool

load_dotenv()

@register_tool('execute_sql_query')
class SQLTool(BaseTool):
    """
    SQL Tool for executing PostgreSQL database queries
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
        User Qwen model to convert natural language to SQL
        """
        create_sql = """
-- Table: tkt_orders
-- Columns:
-- order_time DATETIME             -- Order date and time
-- account_id INT                  -- ID of the user who booked
-- gov_id VARCHAR(18)              -- ID of the ticket user (e.g., ID card number)
-- gender VARCHAR(10)              -- Gender of the ticket user
-- age INT                         -- Age of the ticket user
-- province VARCHAR(30)            -- Province of the ticket user
-- SKU VARCHAR(100)                -- Product SKU name
-- product_serial_no VARCHAR(30)   -- Product ID
-- eco_main_order_id VARCHAR(20)   -- Order ID
-- sales_channel VARCHAR(20)       -- Sales channel
-- status VARCHAR(30)              -- Product status (used / unused)
-- order_value DECIMAL(10,2)       -- Order amount
-- quantity INT                    -- Quantity of the product
-- use_time TIMESTAMP              -- Time of ticket use, default if unused
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
        response = dashscope.completions.create(
            model=self.llm_cfg["model"],
            prompt=prompt,
            temperature=self.llm_cfg["temperature"],
            max_tokens=300
        )

        # Extract SQL from response
        if response and len(response.choices) > 0:
            sql_text = response.choices[0].text.strip()
            # Remove ```sql and ``` suffix
            if sql_text.startswith("```sql"):
                sql_text = sql_text[6:].strip()
            if sql_text.endswith("```"):
                sql_text = sql_text[:-3].strip()
            return sql_text

        return ""

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

        # 先把结果转换成简短的 JSON 或表格文本，传给 LLM
        # 注意不要直接传太大数据，选前几行或做聚合
        preview_results = results[:10]  # 取前10条数据
        results_str = json.dumps(preview_results, ensure_ascii=False)

        prompt = f"""
    You are a helpful assistant for a theme park ticket system.
    User asked: "{original_query}"
    The database query returned the following results (first 10 rows):
    {results_str}

    Please provide a clear, concise answer to the user's question based on the data above.
    """
        # 调用 Qwen LLM
        response = dashscope.completions.create(
            model=self.llm_cfg["model"],
            prompt=prompt,
            temperature=0.2,
            max_tokens=300
        )

        if response and len(response.choices) > 0:
            answer = response.choices[0].text.strip()
            # 去掉可能的 ``` 等标记
            if answer.startswith("```"):
                answer = answer[3:].strip()
            if answer.endswith("```"):
                answer = answer[:-3].strip()
            return answer

        return "Could not generate an answer from the query results."
