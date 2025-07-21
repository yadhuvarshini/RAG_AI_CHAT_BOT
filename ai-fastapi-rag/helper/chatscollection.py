from db.mongo import chats_collection
import uuid
from datetime import datetime

async def create_chat(user_id, chat_name):
    chat_id = str(uuid.uuid4())
    chat_doc = {
        "user_id" : user_id,
        "chat_id": chat_id,
        "chat_name":chat_name,
        "created_at":datetime.utcnow(),
        "last_asked":datetime.utcnow()
    }
    await chats_collection.insert_one(chat_doc)
    return chat_id