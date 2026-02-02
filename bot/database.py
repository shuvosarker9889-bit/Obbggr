# -*- coding: utf-8 -*-
"""
🗄️ Database Module - MongoDB Integration
Handles all database operations with automatic reconnection
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bot.config import config

logger = logging.getLogger(__name__)

# Global database instances
db_client: Optional[AsyncIOMotorClient] = None
database = None


async def init_database():
    """
    Initialize MongoDB connection
    Auto-reconnect on failure
    """
    global db_client, database
    
    retries = 0
    while retries < config.MAX_RETRIES:
        try:
            logger.info(f"🔄 Attempting database connection... (Attempt {retries + 1}/{config.MAX_RETRIES})")
            
            # Create MongoDB client
            db_client = AsyncIOMotorClient(
                config.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True
            )
            
            # Test connection
            await db_client.admin.command('ping')
            
            # Get database
            database = db_client[config.DATABASE_NAME]
            
            # Create indexes for better performance
            await create_indexes()
            
            logger.info("✅ Database connected successfully!")
            return database
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            retries += 1
            logger.error(f"❌ Database connection failed: {e}")
            if retries >= config.MAX_RETRIES:
                raise Exception("Failed to connect to MongoDB after multiple attempts")
            await asyncio.sleep(2)
    
    raise Exception("Database initialization failed")


async def create_indexes():
    """Create database indexes for optimization"""
    try:
        # Content collection indexes
        await database.contents.create_index("copy_id", unique=True)
        await database.contents.create_index("content_type")
        await database.contents.create_index("created_at")
        
        # User delivery tracking indexes
        await database.user_deliveries.create_index([("user_id", 1), ("copy_id", 1)], unique=True)
        await database.user_deliveries.create_index("delivered_at")
        
        # Extra channels index
        await database.extra_channels.create_index("channel_id", unique=True)
        
        logger.info("✅ Database indexes created successfully!")
    except Exception as e:
        logger.warning(f"⚠️ Index creation warning: {e}")


# ═══════════════════════════════════════════════════════════════
# 📝 CONTENT MANAGEMENT
# ═══════════════════════════════════════════════════════════════

async def save_content(copy_id: str, message_id: int = None, link: str = None, 
                       content_type: str = "video") -> Dict:
    """
    Save video or link to database
    
    Args:
        copy_id: Unique identifier for content
        message_id: Telegram message ID (for videos)
        link: External link (for links)
        content_type: "video" or "link"
    """
    try:
        content_data = {
            "copy_id": copy_id,
            "content_type": content_type,
            "message_id": message_id,
            "link": link,
            "created_at": datetime.utcnow(),
            "channel_id": config.CONTENT_CHANNEL_ID
        }
        
        # Upsert: Update if exists, insert if new
        result = await database.contents.update_one(
            {"copy_id": copy_id},
            {"$set": content_data},
            upsert=True
        )
        
        logger.info(f"✅ Content saved: {copy_id} ({content_type})")
        return content_data
        
    except Exception as e:
        logger.error(f"❌ Failed to save content: {e}")
        raise


async def get_content(copy_id: str) -> Optional[Dict]:
    """
    Retrieve content by copy_id
    
    Returns:
        Content data or None if not found
    """
    try:
        content = await database.contents.find_one({"copy_id": copy_id})
        return content
    except Exception as e:
        logger.error(f"❌ Failed to get content: {e}")
        return None


async def delete_content(copy_id: str) -> bool:
    """Delete content from database"""
    try:
        result = await database.contents.delete_one({"copy_id": copy_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"❌ Failed to delete content: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# 👥 USER DELIVERY TRACKING (Duplicate Prevention)
# ═══════════════════════════════════════════════════════════════

async def check_already_delivered(user_id: int, copy_id: str) -> bool:
    """
    Check if user already received this content
    
    Returns:
        True if already delivered, False otherwise
    """
    try:
        existing = await database.user_deliveries.find_one({
            "user_id": user_id,
            "copy_id": copy_id
        })
        return existing is not None
    except Exception as e:
        logger.error(f"❌ Failed to check delivery: {e}")
        return False


async def mark_as_delivered(user_id: int, copy_id: str, message_id: int) -> Dict:
    """
    Mark content as delivered to user
    Prevents duplicate delivery
    """
    try:
        delivery_data = {
            "user_id": user_id,
            "copy_id": copy_id,
            "message_id": message_id,
            "delivered_at": datetime.utcnow()
        }
        
        # Upsert to handle re-delivery
        await database.user_deliveries.update_one(
            {"user_id": user_id, "copy_id": copy_id},
            {"$set": delivery_data},
            upsert=True
        )
        
        logger.info(f"✅ Delivery tracked: User {user_id} - Content {copy_id}")
        return delivery_data
        
    except Exception as e:
        logger.error(f"❌ Failed to track delivery: {e}")
        raise


async def remove_previous_delivery(user_id: int, copy_id: str) -> bool:
    """
    Remove previous delivery record
    Used when user requests same content again
    """
    try:
        result = await database.user_deliveries.delete_one({
            "user_id": user_id,
            "copy_id": copy_id
        })
        
        if result.deleted_count > 0:
            logger.info(f"♻️ Removed previous delivery: User {user_id} - Content {copy_id}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to remove delivery: {e}")
        return False


async def get_user_deliveries(user_id: int, limit: int = 50) -> List[Dict]:
    """Get user's delivery history"""
    try:
        deliveries = await database.user_deliveries.find(
            {"user_id": user_id}
        ).sort("delivered_at", -1).limit(limit).to_list(length=limit)
        
        return deliveries
    except Exception as e:
        logger.error(f"❌ Failed to get deliveries: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# 📢 EXTRA CHANNELS MANAGEMENT (Admin Panel)
# ═══════════════════════════════════════════════════════════════

async def add_extra_channel(channel_id: int, channel_name: str = None) -> bool:
    """Add extra force join channel"""
    try:
        channel_data = {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "added_at": datetime.utcnow(),
            "is_active": True
        }
        
        await database.extra_channels.update_one(
            {"channel_id": channel_id},
            {"$set": channel_data},
            upsert=True
        )
        
        logger.info(f"✅ Extra channel added: {channel_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add channel: {e}")
        return False


async def remove_extra_channel(channel_id: int) -> bool:
    """Remove extra force join channel"""
    try:
        result = await database.extra_channels.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"❌ Failed to remove channel: {e}")
        return False


async def get_extra_channels() -> List[int]:
    """Get list of all extra force join channels"""
    try:
        channels = await database.extra_channels.find(
            {"is_active": True}
        ).to_list(length=100)
        
        return [ch["channel_id"] for ch in channels]
    except Exception as e:
        logger.error(f"❌ Failed to get channels: {e}")
        return []


async def toggle_channel_status(channel_id: int, is_active: bool) -> bool:
    """Enable/disable extra channel without deleting"""
    try:
        result = await database.extra_channels.update_one(
            {"channel_id": channel_id},
            {"$set": {"is_active": is_active}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"❌ Failed to toggle channel: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# 📊 STATISTICS
# ═══════════════════════════════════════════════════════════════

async def get_stats() -> Dict:
    """Get bot statistics"""
    try:
        total_contents = await database.contents.count_documents({})
        total_videos = await database.contents.count_documents({"content_type": "video"})
        total_links = await database.contents.count_documents({"content_type": "link"})
        total_deliveries = await database.user_deliveries.count_documents({})
        unique_users = len(await database.user_deliveries.distinct("user_id"))
        extra_channels_count = await database.extra_channels.count_documents({"is_active": True})
        
        return {
            "total_contents": total_contents,
            "total_videos": total_videos,
            "total_links": total_links,
            "total_deliveries": total_deliveries,
            "unique_users": unique_users,
            "extra_channels": extra_channels_count
        }
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        return {}


# Import asyncio for reconnection delays
import asyncio
