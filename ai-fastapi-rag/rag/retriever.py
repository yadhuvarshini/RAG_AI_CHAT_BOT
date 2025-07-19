import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(
    path="chroma_store",
)

collection = client.get_or_create_collection(name="documents")

def store_documents(chunks, embedded_chunks):
    for i,chunk in enumerate(chunks):
        collection.add(documents=[chunk], ids=[f"chunk_{i}"])
    return True

def retrieve_similar_docs(query, embed_fn):
    return collection.query(
        query_texts=[query],
        n_results=5)