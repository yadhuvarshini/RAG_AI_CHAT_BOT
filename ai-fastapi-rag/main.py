# main.py
import os
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv
from processors.file_processor import extract_text
from rag.embedder import get_embedding_function
from rag.retriever import store_documents, retrieve_similar_docs
from fastapi.middleware.cors import CORSMiddleware
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Gemini integration
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        temp_path = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Extract and embed
        text = extract_text(temp_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(text)
        embed_fn = get_embedding_function()
        store_documents(chunks, embed_fn)

        return {"message": "File processed and embedded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    try:
        embed_fn = get_embedding_function()
        results = retrieve_similar_docs(question, embed_fn)
        docs = results['documents'][0]
        if not docs:
            return {"message": "No relevant documents found."}
        context = "\n\n".join(docs)
        prompt = f"""
You are an intelligent assistant. Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        response = llm.invoke(prompt)

        return {
            "question": question,
            "gemini_answer": response.content
        }
    except Exception as e:
        return {"error": str(e)}
