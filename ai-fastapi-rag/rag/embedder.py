# rag/embedder.py
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()  # Load .env file

def get_embedding_function():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",  # ✅ use 'model', not 'model_name'
        google_api_key=api_key
    )