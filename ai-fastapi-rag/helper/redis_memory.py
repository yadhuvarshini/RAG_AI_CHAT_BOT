from datetime import datetime
import json
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

async def store_memory(redis: Redis, chat_id: str, question: str, answer: str):
    """Store conversation in Redis using async methods"""
    try:
        # Create conversation record
        conversation = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Use async Redis methods
        await redis.rpush(
            f"chat:{chat_id}:conversations",
            json.dumps(conversation)
        )
        
        await redis.hset(
            f"chat:{chat_id}:last",
            mapping={
                "question": question,
                "answer": answer,
                "updated_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Stored memory for chat {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Memory storage error: {str(e)}")
        raise

async def get_memory(redis: Redis, chat_id: str, limit: int = 10):
    """Retrieve conversation history using async methods"""
    try:
        history = await redis.lrange(
            f"chat:{chat_id}:conversations",
            0,
            limit - 1
        )
        return [json.loads(item) for item in history]
    except Exception as e:
        logger.error(f"Memory retrieval error: {str(e)}")
        return []