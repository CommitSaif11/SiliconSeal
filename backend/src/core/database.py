"""
Database Connection Management
Async MongoDB using Motor driver
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)


class Database:
    """
    MongoDB connection manager for Saif's system
    
    Handles:
        - Connection pooling
        - Database initialization
        - Collection access
    """
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls):
        """
        Connect to MongoDB Atlas
        
        Note for Saif:
            Called once at app startup in main.py
        """
        try:
            logger.info("Connecting to MongoDB for Saif...")
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10
            )
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            await cls.client.admin.command('ping')
            logger.info("✅ MongoDB connected successfully for Saif!")
            logger.info(f"📦 Database: {settings.MONGODB_DB_NAME}")
            await cls.create_indexes()
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed for Saif: {str(e)}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client is not None:
            cls.client.close()
            logger.info("MongoDB connection closed for Saif")
    
    @classmethod
    async def create_indexes(cls):
        """Create database indexes for better performance"""
        if cls.db is None:
            return
        try:
            await cls.db.verification_logs.create_index("timestamp")
            await cls.db.verification_logs.create_index("part_id")
            await cls.db.verification_logs.create_index("verdict")
            await cls.db.kb_entries.create_index("part_id", unique=True)
            await cls.db.agent_logs.create_index("timestamp")
            logger.info("✅ Database indexes created for Saif")
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {str(e)}")
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.db is None:
            raise RuntimeError("Database not connected! Call Database.connect() first")
        return cls.db


async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency injection helper"""
    return Database.get_db()