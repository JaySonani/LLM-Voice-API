"""Unit tests for scrapper tool."""

import pytest
from unittest.mock import Mock, patch
import requests

from app.tools.scrapper_tool import fetch_page_text


class TestScrapperTool:
    """Test suite for web scraping utilities."""

    @patch('app.tools.scrapper_tool.requests.get')
    def test_fetch_page_text_success(self, mock_get):
        """Test successful page text extraction."""
        # WHAT: Extract text content from a web page
        # WHY: Validates web scraping functionality for voice profile generation
        mock_response = Mock()
        mock_response.text = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Welcome</h1>
                <p>This is test content.</p>
                <script>console.log('ignored');</script>
                <style>.hidden { display: none; }</style>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        text = fetch_page_text("https://example.com")
        
        assert "Welcome" in text
        assert "This is test content" in text
        assert "console.log" not in text  # Scripts removed
        assert ".hidden" not in text  # Styles removed
        mock_get.assert_called_once_with("https://example.com", timeout=10)
