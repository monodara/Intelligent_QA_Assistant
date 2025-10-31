
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import json
import os

# Make sure the path is correct to import SQLTool
from bot.tools.sql_tool import SQLTool

class TestSQLTool(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.sql_tool = SQLTool()

    @patch('bot.tools.sql_tool.pd.read_sql')
    def test_execute_sql_success(self, mock_read_sql):
        """Test successful execution of a SQL query."""
        # Mocking the DataFrame that would be returned by pandas
        mock_df = pd.DataFrame({
            'visit_date': ['2023-10-01'],
            'visitor_count': [150]
        })
        mock_read_sql.return_value = mock_df

        sql_query = "SELECT visit_date, COUNT(*) as visitor_count FROM visit_flow GROUP BY visit_date;"
        result = self.sql_tool.execute_sql(sql_query)

        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['results'], mock_df.to_dict(orient="records"))
        mock_read_sql.assert_called_once_with(sql_query, self.sql_tool.engine)

    @patch('bot.tools.sql_tool.pd.read_sql')
    def test_execute_sql_failure(self, mock_read_sql):
        """Test failed execution of a SQL query."""
        # Mocking an exception during SQL execution
        error_message = "Test SQL execution error"
        mock_read_sql.side_effect = Exception(error_message)

        sql_query = "SELECT * FROM non_existent_table;"
        result = self.sql_tool.execute_sql(sql_query)

        self.assertFalse(result['success'])
        self.assertIn(error_message, result['error'])
        mock_read_sql.assert_called_once_with(sql_query, self.sql_tool.engine)

    @patch('dashscope.completions.create')
    def test_analyze_results_with_data(self, mock_completions_create):
        """Test analysis of results when data is present."""
        # Mocking the LLM response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].text = "On October 1st, there were 150 visitors."
        mock_completions_create.return_value = mock_response

        results = [{'visit_date': '2023-10-01', 'visitor_count': 150}]
        original_query = "How many visitors were there on October 1st?"
        
        answer = self.sql_tool.analyze_results(results, original_query)

        self.assertEqual(answer, "On October 1st, there were 150 visitors.")
        
        # Verify that the prompt passed to the LLM is as expected
        mock_completions_create.assert_called_once()
        call_args = mock_completions_create.call_args
        prompt = call_args[1]['prompt']
        self.assertIn(original_query, prompt)
        self.assertIn(json.dumps(results, ensure_ascii=False), prompt)

    def test_analyze_results_no_data(self):
        """Test analysis of results when no data is found."""
        answer = self.sql_tool.analyze_results([], "Any query")
        self.assertEqual(answer, "No data found for your query.")

    @patch('dashscope.completions.create')
    def test_analyze_results_llm_failure(self, mock_completions_create):
        """Test analysis of results when the LLM fails to generate an answer."""
        # Mocking a failed LLM response
        mock_completions_create.return_value = None

        results = [{'visit_date': '2023-10-01', 'visitor_count': 150}]
        original_query = "How many visitors were there on October 1st?"
        
        answer = self.sql_tool.analyze_results(results, original_query)

        self.assertEqual(answer, "Could not generate an answer from the query results.")

if __name__ == '__main__':
    unittest.main()
