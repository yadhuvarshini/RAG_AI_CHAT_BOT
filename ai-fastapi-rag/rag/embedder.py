from langchain_community.embeddings import HuggingFaceEmbeddings  # Updated import
from typing import Union, List
import numpy as np

class AsyncHuggingFaceEmbeddings(HuggingFaceEmbeddings):
    """Wrapper to add async methods to HuggingFaceEmbeddings"""
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async embed documents"""
        return self.embed_documents(texts)
    
    async def aembed_query(self, text: str) -> List[float]:
        """Async embed query"""
        return self.embed_query(text)

def get_embedding_function(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> AsyncHuggingFaceEmbeddings:
    """Returns embedding function with async support"""
    return AsyncHuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},  # Change to 'cuda' if you have GPU
        encode_kwargs={'normalize_embeddings': True}
    )