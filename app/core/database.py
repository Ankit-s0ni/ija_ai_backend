from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DATABASE]

async def test_connection():
    """Test MongoDB connection"""
    try:
        # Test the connection
        await client.admin.command('ping')
        logger.info("MongoDB connection successful!")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False
