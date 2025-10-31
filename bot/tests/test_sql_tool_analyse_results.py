import pytest
from ..tools.sql_tool import SQLTool

@pytest.fixture
def sql_tool():
    return SQLTool()

def test_analyze_results_real_llm(sql_tool):
    # SQL query execution will return only one record (simulating LIMIT 1)
    results = [
        {"visit_date": "2024-07-02", "total_visitors": 3}
    ]
    query = "What day had the highest visitor flow last year?"

    # Call real LLM to analyze results
    answer = sql_tool.analyze_results(results, query)

    print("LLM Analysis Result:", answer)

    # Check if the answer contains expected date
    assert "2024-07-02" in answer
