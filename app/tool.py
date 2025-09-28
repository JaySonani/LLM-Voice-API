"""Web scraping utilities for extracting text content from web pages."""

import requests
from bs4 import BeautifulSoup

def fetch_page_text(url: str) -> str:
    """
    Fetches the visible text content from a given URL.

    Args:
        url (str): The web page URL.

    Returns:
        str: Extracted plain text from the page.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts, styles, etc.
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()

        text = soup.get_text(separator=" ", strip=True)
        return text

    except requests.RequestException as e:
        return f"Error fetching {url}: {e}"

