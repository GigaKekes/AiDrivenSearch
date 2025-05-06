import time
import requests

from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from markdownify import markdownify as md 


from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.text_splitter import Language
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import cross_encoder

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
    
def extract_relevant(query: str, text: str, min_per_chunk: int = 256, max_document_length: int=1500) -> str:
    """
    Extracts relevant information from the text using 8-layered BERT
    
    :param query (str): The query to search for in the text.
    :param text (str): The text to extract information from.
    :param min_per_chunk (int): The minimum number of characters per chunk.
    :param max_document_length (int): The maximum length of the document.
    
    :return str: The extracted information.
    """
    
    splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.MARKDOWN, 
    chunk_size=min_per_chunk,
    chunk_overlap=min_per_chunk//2
    )
    
    chunks = splitter.split_text(text)
    
    pairs = [(query, chunk) for chunk in chunks]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    relevant_chunks = []
    length = 0
    for score, chunk in ranked:
        if length + len(chunk) > max_document_length:
            break
        relevant_chunks.append(chunk)
        length += len(chunk)
    return "\n\n".join(relevant_chunks)
