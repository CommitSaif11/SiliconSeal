"""
Database Connection Management
Async MongoDB using Motor driver
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
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
            logger.info(f"Connecting to MongoDB for Saif...")
            
            # Create async MongoDB client
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                maxPoolSize=10  # Connection pool size
            )
            
            # Get database
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # Test connection
            await cls.client.admin.command('ping')
            
            logger.info(f"✅ MongoDB connected successfully for Saif!")
            logger.info(f"📦 Database: {settings.MONGODB_DB_NAME}")
            
            # Create indexes (for better query performance)
            await cls.create_indexes()
            
        except Exception as e:
            logger. error(f"❌ MongoDB connection failed for Saif: {str(e)}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """
        Disconnect from MongoDB
        
        Note for Saif:
            Called at app shutdown in main.py
        """
        if cls.client is not None:  # FIX: Changed from "if cls.client"
            cls.client.close()
            logger.info("MongoDB connection closed for Saif")
    
    @classmethod
    async def create_indexes(cls):
        """
        Create database indexes for better performance
        
        Note for Saif:
            Indexes speed up queries on frequently searched fields
        """
        # FIX: Changed from "if not cls.db" to "if cls.db is None"
        if cls.db is None:
            return
        
        try:
            # Verification logs - index by timestamp and part_id
            await cls.db. verification_logs.create_index("timestamp")
            await cls.db.verification_logs.create_index("part_id")
            await cls.db.verification_logs. create_index("verdict")
            
            # KB entries - index by part_id (unique)
            await cls.db. kb_entries.create_index("part_id", unique=True)
            
            # Agent logs - index by timestamp
            await cls.db.agent_logs.create_index("timestamp")
            
            logger.info("✅ Database indexes created for Saif")
            
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {str(e)}")
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """
        Get database instance
        
        Returns:
            AsyncIOMotorDatabase instance
        
        Note for Saif:
            Use this in your API endpoints to access collections
        """
        # FIX: Changed from "if not cls.db" to "if cls.db is None"
        if cls.db is None:
            raise RuntimeError("Database not connected!  Call Database.connect() first")
        return cls.db


# Convenience function for Saif's endpoints
async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency injection helper for FastAPI
    
    Usage in endpoints:
        @router.get("/scan")
        async def scan(db: AsyncIOMotorDatabase = Depends(get_database)):
            await db.verification_logs.insert_one(...)
    """
    return Database.get_db()