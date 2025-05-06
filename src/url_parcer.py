from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from markdownify import markdownify as md 
import requests 

def parse_url(url: str) -> str:
    """
    Parses a URL and returns the HTML content in markdown format.
    
    :param url (str): The URL to parse.
    :return str: A markdown representation of the HTML content.
    """
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
    
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    main_content = str(soup.body)
    
    markdown_content = md(main_content)
    
    return markdown_content
    
def extract_relevant(text: str, min_tokens_per_chunk: int) -> str:
    """
    Extracts relevant information from the text using 8-layered BERT
    
    :param text (str): The text to extract information from.
    :return str: The extracted information.
    """


    
# Example usage
if __name__ == "__main__":
    url = f"https://ru.wikipedia.org/wiki/%D0%98%D1%81%D0%BA%D1%83%D1%81%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9_%D0%B8%D0%BD%D1%82%D0%B5%D0%BB%D0%BB%D0%B5%D0%BA%D1%82"
    print(parse_url(url))
    
    