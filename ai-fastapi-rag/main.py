import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from processors.file_processor import extract_text
from rag.embedder import get_embedding_function
from rag.retriever import store_documents, retrieve_similar_docs
from fastapi.middleware.cors import CORSMiddleware
from langchain.text_splitter import RecursiveCharacterTextSplitter
from auth.auth import router as auth_router, SECRET_KEY, ALGORITHM
from db.mongo import users_collection, chats_collection
from jose import jwt, JWTError
from helper.chatscollection import create_chat
from helper.redis_memory import store_memory, get_memory
from redis import asyncio as aioredis
import json
from together import Together
from pydantic import BaseModel, constr, validator
from fastapi import status
from fastapi.middleware import Middleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import BackgroundTasks
from redis.exceptions import RedisError
from pymongo.errors import PyMongoError
import logging
from langchain_huggingface import HuggingFaceEmbeddings  # New import path

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ['.pdf', '.docx', '.txt', '.pptx']
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Initialize Redis for rate limiting and memory
redis = aioredis.from_url(
    "redis://localhost",
    decode_responses=True,  # Correct parameter name
    encoding="utf-8",
    socket_timeout=5
)
# Initialize Together client with async support
client = Together(api_key=TOGETHER_API_KEY, timeout=30, max_retries=3)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Pydantic models for input validation
class ChatCreateRequest(BaseModel):
    chat_name: constr(min_length=1, max_length=100)

class ProcessRequest(BaseModel):
    chat_id: constr(min_length=24, max_length=24)  # Assuming MongoDB ObjectId length
    file: UploadFile

    @validator('file')
    def validate_file(cls, file):
        if not any(file.filename.endswith(ext) for ext in ALLOWED_FILE_TYPES):
            raise ValueError("Unsupported file type")
        return file

class AskRequest(BaseModel):
    chat_id: constr(min_length=24, max_length=24)
    question: constr(min_length=1, max_length=1000)

app = FastAPI()

# Add HTTPS redirection in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Rate limiting exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests. Please try again later."},
    )

# Dependency for authentication
# Update the get_current_user dependency
async def get_current_user(request: Request):
    # Check both headers and form data for token
    auth_header = request.headers.get("Authorization")
    form_data = await request.form()
    
    token = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    elif "token" in form_data:
        token = form_data["token"]
    
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Update CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:8501","http://nodejs","http://localhost:5500" ],  # Add Node.js server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function for file validation
async def validate_file_size(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {MAX_FILE_SIZE/1024/1024}MB"
        )

# Background task for cleanup
async def cleanup_temp_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.error(f"Error cleaning up temp file {path}: {str(e)}")

@app.post("/test_upload")
@limiter.limit("5/minute")
async def test_upload(
    request: Request,
    chat_id: str = Form(...),
    file: UploadFile = File(...)
):
    return {
        "chat_id": chat_id,
        "filename": file.filename
    }

@app.get("/chats")
@limiter.limit("10/minute")
async def list_chats(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    try:
        chats = await chats_collection.find({"user_id": current_user["email"]}).sort("created_at", -1).to_list(length=100)
        return [{
            "chat_id": chat["chat_id"],
            "chat_name": chat["chat_name"],
            "created_at": chat["created_at"]
        } for chat in chats]
    except Exception as e:
        logger.error(f"Error listing chats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/chat")
@limiter.limit("3/minute")
async def create_new_chat(
    request: Request,
    chat_data: ChatCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        chat_id = await create_chat(current_user["email"], chat_data.chat_name)
        logger.info(f"Created new chat {chat_id} for user {current_user['email']}")
        return {"chat_id": chat_id}
    except Exception as e:
        logger.error(f"Error creating chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating chat")

@app.post("/process")
@limiter.limit("5/minute")
async def process_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chat_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file size
        await validate_file_size(file)

        # Verify chat exists
        chat = await chats_collection.find_one({"chat_id": chat_id, "user_id": current_user["email"]})
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Save to temp file
        temp_path = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)

        try:
            # Write file to disk
            with open(temp_path, "wb") as f:
                f.write(await file.read())

            # Extract text
            text = extract_text(temp_path)
            if not text:
                raise HTTPException(status_code=400, detail="Could not extract text from file")

            # Split into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
            chunks = splitter.split_text(text)
            if not chunks:
                raise HTTPException(status_code=400, detail="No valid text chunks extracted")

            # Store embeddings
            embed_fn = get_embedding_function()
            await store_documents(chunks, embed_fn, current_user["email"], chat_id)

            # Generate summary
            summary_prompt = f"Summarize this document in 3-4 lines:\n\n{text[:5000]}"
            completion = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.1",
                messages=[{"role": "user", "content": summary_prompt}]
            )
            summary_text = completion.choices[0].message.content.strip()

            # Store summary in Redis
            await redis.set(f"summary:{chat_id}", summary_text)

            # Return success
            return {
                "status": "success",
                "message": "File processed and embedded successfully",
                "filename": file.filename,
                "summary": summary_text
            }

        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            # Clean up temp file
            background_tasks.add_task(cleanup_temp_file, temp_path)

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")


@app.post("/ask")
async def ask_question(
    request: Request,
    question: str = Form(...),
    chat_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    async def generate_stream(prompt: str, chat_id: str, question: str):
        """Inner function to handle the streaming response"""
        full_answer = ""
        try:
            print(f"\n---PROMPT---\n{prompt}\n---END PROMPT---\n")  # Debug prompt

            # Create the completion asynchronously
            response = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.1",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            # Process the  iterator sync way
            for chunk in response:
                if chunk.choices:
                    text = chunk.choices[0].delta.content or ""
                    print(f"RAW CHUNK: {text}")  
                    full_answer += text
                    yield json.dumps({
                        "type": "answer_chunk",
                        "content": text
                    }) + "\n"

            print(f"\n---FULL ANSWER---\n{full_answer}\n---END ANSWER---\n")  # Debug final answer
            logger.info(f"Final answer: {full_answer}")


            # Store conversation after successful completion
            try:
                await store_memory(redis, chat_id, question, full_answer)
            except Exception as e:
                logger.error(f"Memory storage failed: {str(e)}")

        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield json.dumps({
                "type": "error",
                "content": "Error generating answer"
            }) + "\n"

    try:
        logger.info(f"Ask request - User: {current_user['email']}, Chat: {chat_id}")

        # 1. Verify chat exists
        chat = await chats_collection.find_one({
            "chat_id": chat_id,
            "user_id": current_user["email"]
        })
        if not chat:
            raise HTTPException(404, "Chat not found")

        # 2. Initialize embedding function
        try:
            embed_fn = get_embedding_function()
            test_embedding = embed_fn.embed_query("test")
            if not test_embedding:
                raise ValueError("Embedding failed")
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise HTTPException(500, "Embedding service unavailable")

        # 3. Retrieve documents
        try:
            results = await retrieve_similar_docs(
                question,
                embed_fn,
                current_user["email"],
                chat_id
            )
            
            if not results["documents"]:
                return {
                    "status": "success",
                    "message": "No relevant documents found",
                    "answer": "I couldn't find any information to answer your question."
                }

            context = "\n\n".join(results["documents"][:3])

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Document error: {str(e)}")
            raise HTTPException(500, "Document processing failed")

        # 4. Generate response
        prompt = f"""Answer based on:
        {context}
        
        Question: {question}
        
        Rules:
        - Be concise
        - Only use provided context
        - Say "I don't know" if unsure
        Answer:"""

        return StreamingResponse(
            generate_stream(prompt, chat_id, question),
            media_type="text/event-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, "Processing failed")
    

@app.get("/chat_summary/{chat_id}")
@limiter.limit("20/minute")
async def get_chat_summary(
    request: Request,
    chat_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Validate chat exists
        chat = await chats_collection.find_one({
            "chat_id": chat_id,
            "user_id": current_user["email"]
        })
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        summary = await redis.get(f"summary:{chat_id}")
        return {"summary": summary or "No summary available."}
    except Exception as e:
        logger.error(f"Error getting chat summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving summary")

@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()
    logger.info("Application shutdown complete")

# Include auth router
app.include_router(auth_router, prefix="/auth")