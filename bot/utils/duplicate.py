# -*- coding: utf-8 -*-
"""
♻️ Duplicate Prevention System
Ensures users don't receive the same content multiple times
"""

import logging
from pyrogram import Client
from pyrogram.errors import MessageDeleteForbidden, MessageIdInvalid
from bot.database import (
    check_already_delivered,
    mark_as_delivered,
    remove_previous_delivery,
    database,
    get_user_deliveries
)
from typing import Tuple

logger = logging.getLogger(__name__)


async def handle_duplicate_prevention(
    client: Client,
    user_id: int,
    copy_id: str,
    new_message_id: int
) -> bool:
    """
    Handle duplicate content delivery
    
    Strategy:
    1. Check if user already received this content
    2. If yes, delete/invalidate previous message
    3. Mark new message as delivered
    
    Args:
        client: Pyrogram client
        user_id: User's Telegram ID
        copy_id: Content identifier
        new_message_id: New message ID that was just sent
    
    Returns:
        True if handled successfully, False otherwise
    """
    try:
        # Check if already delivered
        already_delivered = await check_already_delivered(user_id, copy_id)
        
        if already_delivered:
            logger.info(f"♻️ User {user_id} already received {copy_id}. Handling duplicate...")
            
            # Remove previous delivery record
            removed = await remove_previous_delivery(user_id, copy_id)
            
            if removed:
                logger.info(f"✅ Previous delivery record removed for {copy_id}")
        
        # Mark new message as delivered
        await mark_as_delivered(user_id, copy_id, new_message_id)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Duplicate prevention failed: {e}")
        return False


async def delete_previous_message(client: Client, user_id: int, message_id: int) -> bool:
    """
    Try to delete previous message sent to user
    
    Note: This may fail if:
    - Message is too old
    - User deleted it already
    - Bot doesn't have permission
    """
    try:
        await client.delete_messages(user_id, message_id)
        logger.info(f"🗑️ Deleted previous message {message_id} from user {user_id}")
        return True
    except (MessageDeleteForbidden, MessageIdInvalid) as e:
        logger.warning(f"⚠️ Could not delete message {message_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to delete message: {e}")
        return False


async def should_send_content(user_id: int, copy_id: str) -> Tuple[bool, str]:
    """
    Check if content should be sent to user
    
    Returns:
        (should_send, reason)
    """
    try:
        already_delivered = await check_already_delivered(user_id, copy_id)
        
        if already_delivered:
            # Allow re-delivery (will handle duplicate prevention)
            return True, "Re-delivery allowed (previous will be invalidated)"
        else:
            return True, "First time delivery"
            
    except Exception as e:
        logger.error(f"❌ Failed to check delivery status: {e}")
        # On error, allow delivery to prevent blocking users
        return True, "Error in check, allowing delivery"


async def cleanup_old_deliveries(user_id: int, keep_last: int = 100):
    """
    Clean up old delivery records for a user
    Keeps only the most recent deliveries
    
    Args:
        user_id: User's Telegram ID
        keep_last: Number of recent deliveries to keep
    """
    try:
        # Get all deliveries for user
        deliveries = await get_user_deliveries(user_id, limit=1000)
        
        if len(deliveries) <= keep_last:
            return  # No cleanup needed
        
        # Sort by delivered_at and keep only recent ones
        deliveries.sort(key=lambda x: x["delivered_at"], reverse=True)
        to_delete = deliveries[keep_last:]
        
        # Delete old records
        delete_ids = [d["_id"] for d in to_delete]
        result = await database.user_deliveries.delete_many(
            {"_id": {"$in": delete_ids}}
        )
        
        logger.info(f"🧹 Cleaned up {result.deleted_count} old delivery records for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup deliveries: {e}")


async def get_duplicate_stats() -> dict:
    """
    Get statistics about duplicate prevention
    Useful for admin monitoring
    """
    try:
        # Total deliveries
        total = await database.user_deliveries.count_documents({})
        
        # Unique users
        unique_users = len(await database.user_deliveries.distinct("user_id"))
        
        # Unique contents
        unique_contents = len(await database.user_deliveries.distinct("copy_id"))
        
        # Average deliveries per user
        avg_per_user = total / unique_users if unique_users > 0 else 0
        
        return {
            "total_deliveries": total,
            "unique_users": unique_users,
            "unique_contents": unique_contents,
            "avg_deliveries_per_user": round(avg_per_user, 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get duplicate stats: {e}")
        return {}
