# -*- coding: utf-8 -*-
"""
🔒 Force Join Checker
Ensures users join required channels before accessing content
"""

import logging
from typing import List, Tuple
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChannelPrivate
from bot.config import config
from bot.database import get_extra_channels

logger = logging.getLogger(__name__)


async def check_user_membership(client: Client, user_id: int, channel_id: int) -> bool:
    """
    Check if user is member of a channel
    
    Returns:
        True if user is member, False otherwise
    """
    try:
        member = await client.get_chat_member(channel_id, user_id)
        # Check if user is member (not kicked/banned)
        return member.status not in ["kicked", "banned", "left"]
    except UserNotParticipant:
        return False
    except (ChatAdminRequired, ChannelPrivate) as e:
        logger.error(f"❌ Bot access error for channel {channel_id}: {e}")
        return True  # Allow access if bot can't check (configuration issue)
    except Exception as e:
        logger.error(f"❌ Membership check failed for {channel_id}: {e}")
        return True  # Allow on error to prevent blocking all users


async def get_all_required_channels() -> List[int]:
    """
    Get all channels user must join
    Includes main force join channel + extra channels
    """
    channels = [config.FORCE_JOIN_CHANNEL_ID]
    
    # Add extra channels from database
    extra = await get_extra_channels()
    channels.extend(extra)
    
    return channels


async def check_all_channels(client: Client, user_id: int) -> Tuple[bool, List[int]]:
    """
    Check user membership in all required channels
    
    Returns:
        (all_joined, not_joined_channels)
    """
    required_channels = await get_all_required_channels()
    not_joined = []
    
    for channel_id in required_channels:
        is_member = await check_user_membership(client, user_id, channel_id)
        if not is_member:
            not_joined.append(channel_id)
    
    all_joined = len(not_joined) == 0
    return all_joined, not_joined


async def create_force_join_keyboard(client: Client, not_joined_channels: List[int]) -> InlineKeyboardMarkup:
    """
    Create inline keyboard with join buttons for channels
    
    Args:
        not_joined_channels: List of channel IDs user hasn't joined
    """
    buttons = []
    
    for channel_id in not_joined_channels:
        try:
            # Get channel info
            chat = await client.get_chat(channel_id)
            channel_name = chat.title or "Channel"
            
            # Create invite link
            if chat.username:
                invite_link = f"https://t.me/{chat.username}"
            else:
                # Try to get invite link
                try:
                    invite_link = await client.export_chat_invite_link(channel_id)
                except:
                    invite_link = None
            
            if invite_link:
                buttons.append([
                    InlineKeyboardButton(
                        f"📢 Join {channel_name}",
                        url=invite_link
                    )
                ])
        except Exception as e:
            logger.error(f"❌ Failed to create button for channel {channel_id}: {e}")
    
    # Add "I've Joined" button
    buttons.append([
        InlineKeyboardButton(
            "✅ আমি জয়েন করেছি / I've Joined",
            callback_data="check_membership"
        )
    ])
    
    return InlineKeyboardMarkup(buttons)


async def send_force_join_message(client: Client, user_id: int, not_joined_channels: List[int]):
    """
    Send force join message to user with join buttons
    """
    keyboard = await create_force_join_keyboard(client, not_joined_channels)
    
    message_text = f"""
🔒 <b>Channel Membership Required</b>

দয়া করে নিচের চ্যানেলগুলোতে জয়েন করুন কন্টেন্ট পেতে:
<i>Please join the channels below to access content:</i>

✅ সব চ্যানেলে জয়েন করার পর <b>"আমি জয়েন করেছি"</b> বাটনে ক্লিক করুন।

🎬 <b>Official Channel:</b> {config.CHANNEL_USERNAME}
"""
    
    try:
        await client.send_message(
            user_id,
            message_text,
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"❌ Failed to send force join message: {e}")


async def verify_bot_admin_access(client: Client, channel_id: int) -> bool:
    """
    Verify bot has admin access to channel
    Needed for membership checking
    """
    try:
        chat = await client.get_chat(channel_id)
        member = await client.get_chat_member(channel_id, "me")
        
        # Bot must be admin or creator
        if member.status in ["administrator", "creator"]:
            logger.info(f"✅ Bot has admin access to channel: {chat.title}")
            return True
        else:
            logger.warning(f"⚠️ Bot is not admin in channel: {chat.title} ({channel_id})")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to verify bot access for {channel_id}: {e}")
        return False


async def check_force_join(client: Client, user_id: int) -> Tuple[bool, InlineKeyboardMarkup]:
    """
    Main force join check function
    
    Returns:
        (can_proceed, join_keyboard_if_needed)
    """
    # Check all required channels
    all_joined, not_joined = await check_all_channels(client, user_id)
    
    if all_joined:
        return True, None
    
    # Create keyboard for channels user hasn't joined
    keyboard = await create_force_join_keyboard(client, not_joined)
    
    return False, keyboard
