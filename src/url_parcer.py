import time
import requests

from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from markdownify import markdownify as md 

from memory_profiler import profile
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.text_splitter import Language

from models import cross_encoder

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

def extract_relevant(query: str, text: str, min_per_chunk: int = 1024, max_document_length: int=7500) -> str:
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
    
    def batched_predict(pairs, batch_size=8):
        results = []
        for i in range(0, len(pairs), batch_size):
            batch = pairs[i:i+batch_size]
            results.extend(cross_encoder.predict(batch))
        return results
    
    pairs = [(query, chunk) for chunk in chunks]
    scores = batched_predict(pairs)
    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    relevant_chunks = []
    length = 0
    for score, chunk in ranked:
        if length + len(chunk) > max_document_length:
            break
        relevant_chunks.append(chunk)
        length += len(chunk)
    return "\n\n".join(relevant_chunks)

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    query = "what is an Artificial Intelligence"
    
    try:
        parsed_content = parse_url(url)
        relevant_text = extract_relevant(query, parsed_content)
        print(relevant_text)
    except Exception as e:
        print(f"Error: {e}")