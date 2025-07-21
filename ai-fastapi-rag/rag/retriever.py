# import chromadb
# from chromadb.utils import embedding_functions

import numpy as np
from db.mongo import documents_collection
from sklearn.metrics.pairwise import cosine_similarity

async def store_documents(chunks, embed_fn, user_id, chat_id):
    print("Type of chunks:", type(chunks))
    print("Type of first chunk:", type(chunks[0]) if chunks else "empty")
    print("Length of chunks:", len(chunks))
    print("Sample chunk content:", chunks[0][:100] if chunks else "empty")
    clean_chunks = [str(chunk) for chunk in chunks if isinstance(chunk, str) and chunk.strip()]
    embeddings = await embed_fn.aembed_documents(clean_chunks)
    
     
    docs_to_store = []

    for i in range(len(chunks)):
        docs_to_store.append({
            "user_id": user_id,
            "chunk": clean_chunks[i],
            "embedding": embeddings[i],
            "chat_id": chat_id,
        })
    
    await documents_collection.insert_many(docs_to_store)


async def retrieve_similar_docs(question, embed_fn, user_id, chat_id, top_k=5):
    try:
        # Get question embedding (sync version)
        question_embedding = embed_fn.embed_query(question)
        question_embedding = np.array(question_embedding).reshape(1, -1)

        # Get documents from MongoDB
        docs = await documents_collection.find({
            "user_id": user_id,
            "chat_id": chat_id
        }).to_list(length=1000)

        # In retrieve_similar_docs()
        print(f"\nRETRIEVED DOCUMENTS: {len(docs)}")
        for i, doc in enumerate(docs[:3]):
            print(f"DOC {i}: {doc['chunk'][:100]}...")

        if not docs:
            return {
                "documents": [],
                "scores": []
            }

        # Prepare embeddings and chunks
        embeddings = []
        chunks = []
        for doc in docs:
            if "embedding" in doc and "chunk" in doc:
                embeddings.append(doc["embedding"])
                chunks.append(doc["chunk"])

        if not embeddings:
            return {
                "documents": [],
                "scores": []
            }

        # Calculate similarities
        embeddings_array = np.array(embeddings)
        sims = cosine_similarity(question_embedding, embeddings_array)[0]
        top_indices = np.argsort(sims)[::-1][:top_k]

        return {
            "documents": [chunks[i] for i in top_indices],
            "scores": [float(sims[i]) for i in top_indices]
        }

    except Exception as e:
        logger.error(f"Document retrieval error: {str(e)}")
        raise HTTPException(500, "Document retrieval failed")
