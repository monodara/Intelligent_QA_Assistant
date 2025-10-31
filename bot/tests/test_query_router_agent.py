import json
import pytest
from unittest.mock import patch
from ..core.query_router import QueryRouter, SQLTool

@pytest.fixture(scope="module")
def router():
    return QueryRouter(rag_engine=None, metadata_store=None, text_index=None, image_index=None)

def test_agent_routes_to_sql(router):
    query = "What was the month with the highest visitor flow last year?"

    mock_sql_result = {
        "success": True,
        "sql": "SELECT ...",
        "answer": "The month with the highest visitor flow was July 2024.",
        "data": [{"visit_date": "2024-07-02", "total_visitors": 3}]
    }

    # Patching the call method of SQLTool to return mock_sql_result
    with patch.object(SQLTool, "call", side_effect=lambda params: json.dumps(mock_sql_result)):
        result = router.route_query(query)

    # SQLTool Check that the tool used is 'execute_sql_query'
    assert result["tool"] == "execute_sql_query"
