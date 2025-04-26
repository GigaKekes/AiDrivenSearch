import os
from dotenv import load_dotenv
from langchain_community.llms import GigaChat
from sentence_transformers import CrossEncoder

load_dotenv()

# GigaChat
llm = GigaChat(
    credentials=os.getenv("GIGACHAT_CREDENTIALS_PATH"),
    verify_ssl_certs=False,
    model="GigaChat:latest"
)

# CrossEncoder
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")