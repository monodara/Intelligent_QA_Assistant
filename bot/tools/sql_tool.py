"""
SQL Tool for querying PostgreSQL database
Used for querying tickets/visitor flow/historical data
"""
import os
import json
import re
from dotenv import load_dotenv

import dashscope
from dashscope import Generation
import pandas as pd
from sqlalchemy import create_engine
from langchain_core.tools import tool

from ..core.ollama_handler import generate_local_answer

load_dotenv()

# Module-level state
ENGINE = create_engine(os.getenv('POSTGRES_CONNECTION_STRING'))
LLM_CFG = {
    "model": "qwen-turbo",
    "api_key": os.getenv("DASHSCOPE_API_KEY", ""),
    "temperature": 0.1,
    "timeout": 30
}

def _nl_to_sql(query: str) -> str:
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
    dashscope.api_key = LLM_CFG["api_key"]
    response = Generation.call(
        model=LLM_CFG["model"],
        prompt=prompt,
        temperature=LLM_CFG["temperature"],
        max_tokens=300
    )

    sql_text = getattr(response, "output", None)

    if not isinstance(sql_text, str):
        sql_text = str(sql_text)

    try:
        data = json.loads(sql_text)
        if "text" in data:
            sql_text = data["text"]
    except Exception:
        pass

    match = re.search(r"```sql\s*(.*?)\s*```", sql_text, re.DOTALL)
    if match:
        sql_text = match.group(1).strip()

    sql_text = sql_text.replace("```", "").strip()
    return sql_text or ""

def _execute_sql(sql: str) -> dict:
    try:
        df = pd.read_sql(sql, ENGINE)
        return {"success": True, "results": df.to_dict(orient="records"), "count": len(df)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _analyze_results(results: list, original_query: str) -> str:
    """
    Use LLM to generate a natural language answer based on SQL query results.
    """
    if not results:
        return "No data found for your query."

    preview_results = results[:10]
    results_str = json.dumps(preview_results, ensure_ascii=False)

    prompt = f'''
            You are an expert data analyst assistant. 
            Answer the user's question based on the SQL query results.
            Answer in the same language as the user query.

            User question: "{original_query}"

            The SQL query returned the following results (first 10 rows or aggregation results):
            {results_str}

            Instructions:
            1. The results may include aggregated or summary data (e.g., MAX, COUNT, etc.).
            2. Even if the SQL result has only one row, provide a complete, concise natural language answer to the user's question.
            3. Focus only on the information in the SQL results.
            4. Keep the answer clear and precise, suitable for end-user understanding.

            Answer:
            '''
    answer = generate_local_answer(prompt)
    return answer

@tool
def text_to_sql(query: str) -> str:
    """Answer queries about visit flow, low/high, slack/peak seasons by converting natural language to SQL, executing it, and analyzing the results."""
    if not query.strip():
        return json.dumps({"success": False, "error": "No SQL query text provided."}, ensure_ascii=False)
    
    sql = _nl_to_sql(query)
    if not sql:
        return json.dumps({"success": False, "error": "Unable to generate SQL"}, ensure_ascii=False)
    
    sql_result = _execute_sql(sql)
    if not sql_result["success"]:
        return {"success": False, "error": sql_result.get("error", "SQL execution failed")}
    return sql_result