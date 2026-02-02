# -*- coding: utf-8 -*-
"""
📹 Content Delivery Handler
Handles video and link delivery with duplicate prevention
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MediaEmpty, MessageIdInvalid
from bot.config import config
from bot.keyboards import get_link_keyboard
from bot.utils.duplicate import handle_duplicate_prevention
import asyncio

logger = logging.getLogger(__name__)


async def deliver_content(client: Client, message: Message, content: dict, copy_id: str):
    """
    Main content delivery function
    Handles both video and link content
    
    Args:
        client: Pyrogram client
        message: User's message
        content: Content data from database
        copy_id: Content identifier
    """
    user_id = message.from_user.id
    content_type = content.get("content_type", "video")
    
    try:
        if content_type == "video":
            await deliver_video(client, message, content, copy_id)
        elif content_type == "link":
            await deliver_link(client, message, content, copy_id)
        else:
            logger.error(f"❌ Unknown content type: {content_type}")
            await message.reply_text(
                "⚠️ Unsupported content type.",
                quote=True
            )
    
    except FloodWait as e:
        logger.warning(f"⏳ Flood wait: {e.value} seconds")
        await asyncio.sleep(e.value)
        # Retry after wait
        await deliver_content(client, message, content, copy_id)
    
    except Exception as e:
        logger.error(f"❌ Content delivery failed: {e}", exc_info=True)
        await message.reply_text(
            "⚠️ কন্টেন্ট ডেলিভারি ব্যর্থ হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।\n\n"
            "<i>Content delivery failed. Please try again.</i>",
            quote=True
        )


async def deliver_video(client: Client, message: Message, content: dict, copy_id: str):
    """
    Deliver video content using copyMessage
    
    Features:
    - Protected content (no forwarding)
    - Duplicate prevention
    - Direct from content channel
    """
    user_id = message.from_user.id
    message_id = content.get("message_id")
    channel_id = content.get("channel_id", config.CONTENT_CHANNEL_ID)
    
    if not message_id:
        logger.error(f"❌ No message_id found for video content: {copy_id}")
        await message.reply_text(
            "⚠️ Video data is incomplete. Please contact admin.",
            quote=True
        )
        return
    
    try:
        # Copy video message from content channel
        sent_message = await client.copy_message(
            chat_id=user_id,
            from_chat_id=channel_id,
            message_id=message_id,
            protect_content=config.PROTECT_CONTENT  # Disable forwarding
        )
        
        logger.info(f"📹 Video delivered: {copy_id} to user {user_id}")
        
        # Handle duplicate prevention
        await handle_duplicate_prevention(
            client,
            user_id,
            copy_id,
            sent_message.id
        )
        
        # Send confirmation message
        await message.reply_text(
            "✅ <b>Video delivered successfully!</b>\n\n"
            "🎬 আপনার ভিডিও পাঠানো হয়েছে।\n"
            "<i>Your video has been sent.</i>\n\n"
            "💡 <b>Note:</b> Forwarding is disabled for security.",
            quote=True
        )
        
    except MediaEmpty:
        logger.error(f"❌ Media empty for message {message_id}")
        await message.reply_text(
            "⚠️ Video not found in channel. It may have been deleted.",
            quote=True
        )
    
    except MessageIdInvalid:
        logger.error(f"❌ Invalid message ID: {message_id}")
        await message.reply_text(
            "⚠️ Video reference is invalid. Please contact admin.",
            quote=True
        )


async def deliver_link(client: Client, message: Message, content: dict, copy_id: str):
    """
    Deliver link content with inline button
    
    Features:
    - Clean link presentation
    - Inline button for easy access
    - Duplicate prevention
    """
    user_id = message.from_user.id
    link = content.get("link")
    
    if not link:
        logger.error(f"❌ No link found for content: {copy_id}")
        await message.reply_text(
            "⚠️ Link data is incomplete. Please contact admin.",
            quote=True
        )
        return
    
    try:
        # Determine link type and create appropriate message
        link_type = detect_link_type(link)
        
        link_message = f"""
🔗 <b>Link Content Ready!</b>

📎 <b>Link Type:</b> {link_type}
🌐 <b>URL:</b> <code>{link}</code>

━━━━━━━━━━━━━━━━
নিচের বাটনে ক্লিক করে লিংক খুলুন।
<i>Click the button below to open the link.</i>
"""
        
        # Create keyboard with link button
        keyboard = get_link_keyboard(link, f"🔗 Open {link_type}")
        
        # Send link message
        sent_message = await message.reply_text(
            link_message,
            reply_markup=keyboard,
            quote=True,
            disable_web_page_preview=True
        )
        
        logger.info(f"🔗 Link delivered: {copy_id} to user {user_id}")
        
        # Handle duplicate prevention
        await handle_duplicate_prevention(
            client,
            user_id,
            copy_id,
            sent_message.id
        )
        
    except Exception as e:
        logger.error(f"❌ Link delivery failed: {e}", exc_info=True)
        await message.reply_text(
            "⚠️ লিংক পাঠাতে ব্যর্থ হয়েছে।\n"
            "<i>Failed to send link.</i>",
            quote=True
        )


def detect_link_type(link: str) -> str:
    """
    Detect type of link for better presentation
    
    Returns:
        Human-readable link type
    """
    link_lower = link.lower()
    
    if "youtube.com" in link_lower or "youtu.be" in link_lower:
        return "YouTube Video"
    elif "drive.google.com" in link_lower:
        return "Google Drive"
    elif "t.me" in link_lower or "telegram" in link_lower:
        return "Telegram Link"
    elif "instagram.com" in link_lower:
        return "Instagram"
    elif "facebook.com" in link_lower or "fb.com" in link_lower:
        return "Facebook"
    elif "twitter.com" in link_lower or "x.com" in link_lower:
        return "Twitter/X"
    elif ".mp4" in link_lower or ".mkv" in link_lower or ".avi" in link_lower:
        return "Video File"
    elif ".pdf" in link_lower:
        return "PDF Document"
    else:
        return "External Link"


# ═══════════════════════════════════════════════════════════════
# CONTENT CHANNEL MONITORING (Auto-capture for Admin)
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.chat(config.CONTENT_CHANNEL_ID) & (filters.video | filters.document | filters.text))
async def content_channel_monitor(client: Client, message: Message):
    """
    Monitor content channel for new uploads
    Auto-generate copy_id and save to database
    Notify admin if enabled
    """
    try:
        from bot.database import save_content
        import uuid
        
        # Generate unique copy_id
        copy_id = str(uuid.uuid4())[:8]  # Short unique ID
        
        # Determine content type
        if message.video or message.document:
            content_type = "video"
            message_id = message.id
            link = None
            
            logger.info(f"📹 New video detected in content channel: Message ID {message_id}")
        
        elif message.text:
            # Check if message contains a link
            entities = message.entities or []
            links = [
                message.text[entity.offset:entity.offset + entity.length]
                for entity in entities
                if entity.type == "url"
            ]
            
            if links:
                content_type = "link"
                message_id = None
                link = links[0]  # Take first link
                
                logger.info(f"🔗 New link detected in content channel: {link}")
            else:
                # Plain text, ignore
                return
        else:
            return
        
        # Save to database
        await save_content(
            copy_id=copy_id,
            message_id=message_id,
            link=link,
            content_type=content_type
        )
        
        logger.info(f"✅ Content auto-saved: {copy_id} ({content_type})")
        
        # Notify admin if enabled
        if config.ENABLE_NOTIFICATIONS:
            await notify_admin_new_content(client, copy_id, content_type, message_id, link)
    
    except Exception as e:
        logger.error(f"❌ Content monitoring failed: {e}", exc_info=True)


async def notify_admin_new_content(client: Client, copy_id: str, content_type: str, 
                                   message_id: int = None, link: str = None):
    """
    Send notification to admin about new content
    Includes copy_id for easy Mini App integration
    """
    try:
        notification_text = f"""
🆕 <b>New Content Added!</b>

📋 <b>Copy ID:</b> <code>{copy_id}</code>
📦 <b>Type:</b> {content_type.upper()}
"""
        
        if message_id:
            notification_text += f"🆔 <b>Message ID:</b> <code>{message_id}</code>\n"
        
        if link:
            notification_text += f"🔗 <b>Link:</b> <code>{link}</code>\n"
        
        notification_text += f"""
━━━━━━━━━━━━━━━━
💡 <b>Next Steps:</b>
1. Copy the Copy ID above
2. Add it to your Google Sheets / Mini App
3. Users can now access this content!

🎬 Content Channel: {config.CONTENT_CHANNEL_ID}
"""
        
        await client.send_message(
            config.ADMIN_ID,
            notification_text
        )
        
        logger.info(f"📬 Admin notified about new content: {copy_id}")
    
    except Exception as e:
        logger.error(f"❌ Failed to notify admin: {e}")
