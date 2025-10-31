
import pytest

from bot.tools.sql_tool import SQLTool

@pytest.fixture
def sql_tool():
    tool = SQLTool()
    return tool

def test_execute_sql_success(sql_tool):
    """
    Test successful SQL query returns results
    """
    sql = "SELECT * FROM visit_flow LIMIT 2;"
    result = sql_tool.execute_sql(sql)

    if not result["success"]:
        print("SQL execution failed:", result["error"])
    
    assert result["success"] is True
    assert "results" in result
    assert isinstance(result["results"], list)
    print("Successfully queried results:", result["results"])

def test_execute_sql_failure(sql_tool):
    """
    Test failed SQL query returns error message
    """
    sql = "SELECT * FROM non_existing_table;"
    result = sql_tool.execute_sql(sql)
    
    assert result["success"] is False
    assert "error" in result
    print("Failed to query information:", result["error"])
