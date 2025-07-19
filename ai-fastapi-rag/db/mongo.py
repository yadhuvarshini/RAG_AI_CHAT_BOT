# backend/db/mongo.py

import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_DB_URI")
DB_NAME = os.getenv("DB_NAME", "document_qna")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
documents_collection = db["documents"]
chunks_collection = db["chunks"]
chats_collection = db["chats"]

# Collections you can now access like:
# db.users, db.documents, db.chunks, db.chats