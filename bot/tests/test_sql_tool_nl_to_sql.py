import pytest
from ..tools.sql_tool import SQLTool
import os

@pytest.fixture
def sql_tool():
    return SQLTool()

def test_nl_to_sql_real_llm(sql_tool):
    query = "What month had the highest visitor flow last year?"
    sql = sql_tool.nl_to_sql(query)
    # Assert that the return value is a string
    assert isinstance(sql, str)
    # Simple check that SQL statement contains SELECT and FROM
    assert "SELECT" in sql.upper()
    assert "FROM" in sql.upper()
