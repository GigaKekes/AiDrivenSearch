import os
from dotenv import load_dotenv
from langchain_community.llms import GigaChat
from sentence_transformers import CrossEncoder, SentenceTransformer

load_dotenv()

# GigaChat LLM
llm = GigaChat(
    credentials=os.getenv("GIGACHAT_CREDENTIALS_PATH"),
    verify_ssl_certs=False,
    model="GigaChat:latest"
)

# CrossEncoder
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

#Bi-encoder
bi_encoder = SentenceTransformer('intfloat/multilingual-e5-base')