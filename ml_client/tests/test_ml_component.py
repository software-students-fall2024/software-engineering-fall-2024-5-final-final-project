"""
Tests for ml-client flask app
"""

import pytest
from unittest.mock import patch, MagicMock
from langchain_community.llms import LlamaCpp
from helpers.respond import (
    initialize_llm,
    respond_to_user_input,
)

MODEL_PATH = "./models/test_model.gguf"
DEFAULT_TEMPERATURE = 0.1


@pytest.fixture
def mock_llm():
    """Fixture for mocking LlamaCpp model."""
    mock_llm = MagicMock(spec=LlamaCpp)
    return mock_llm


class Tests:

    def test_sanity_check(self):
        """
        Test debugging... making sure that we can run a simple test that always passes.
        """
        expected = True
        actual = True
        assert actual == expected, "Expected True to be equal to True!"


    def test_respond_to_user_input(self, mock_llm):
        """Test responding to user input."""

        mock_llm.invoke.return_value = "Response from LLM"

        response = respond_to_user_input("What is the capital of France?", mock_llm)

        assert response == "Response from LLM"
        mock_llm.invoke.assert_called_with(
            "Q: What is the capital of France? A:",
            max_tokens=32,
            stop=["Q:", "\n"],
            echo=True
        )

    def test_respond_to_user_input_timeout(self, mock_llm):
        """Test response when there is a timeout."""

        mock_llm.invoke.side_effect = TimeoutError
        response = respond_to_user_input("What is the capital of France?", mock_llm)
        
        assert response == "The request timed out. Please try again with a shorter input."


    def test_respond_to_user_input_runtime_error(self, mock_llm):
        """Test response when there is a runtime error."""

        mock_llm.invoke.side_effect = RuntimeError
        response = respond_to_user_input("What is the capital of France?", mock_llm)
        
        assert response == "An error occurred while processing your request."
