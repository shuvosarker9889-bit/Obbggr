# -*- coding: utf-8 -*-
"""
🚀 Start Handler - Deep Link & Welcome
Handles /start command and deep links
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from bot.config import config
from bot.keyboards import get_start_keyboard, get_help_keyboard
from bot.utils.force_join import check_force_join, send_force_join_message
from bot.database import get_content
from bot.handlers.content import deliver_content

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """
    Handle /start command
    Supports deep links: /start content_COPY_ID
    """
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        
        # Check for deep link parameter
        if len(message.command) > 1:
            param = message.command[1]
            
            # Deep link format: content_COPY_ID
            if param.startswith("content_"):
                copy_id = param.replace("content_", "")
                logger.info(f"🔗 Deep link detected: User {user_id} requesting content {copy_id}")
                
                # Handle content delivery
                await handle_content_request(client, message, copy_id)
                return
        
        # Regular /start (no deep link)
        await send_welcome_message(client, message)
        
    except Exception as e:
        logger.error(f"❌ Start command failed: {e}", exc_info=True)
        await message.reply_text(
            "⚠️ An error occurred. Please try again or contact support.",
            quote=True
        )


async def send_welcome_message(client: Client, message: Message):
    """Send welcome message to user"""
    user_name = message.from_user.first_name
    
    welcome_text = config.WELCOME_MESSAGE
    
    try:
        await message.reply_text(
            welcome_text,
            reply_markup=get_start_keyboard(),
            quote=True
        )
        logger.info(f"👋 Welcome message sent to {user_name} ({message.from_user.id})")
    except Exception as e:
        logger.error(f"❌ Failed to send welcome message: {e}")


async def handle_content_request(client: Client, message: Message, copy_id: str):
    """
    Handle content delivery request from deep link
    
    Flow:
    1. Check force join
    2. Fetch content from database
    3. Deliver content (video or link)
    4. Handle duplicates
    """
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    try:
        # Step 1: Check force join
        can_proceed, join_keyboard = await check_force_join(client, user_id)
        
        if not can_proceed:
            logger.info(f"🔒 User {user_id} not joined required channels")
            
            await message.reply_text(
                f"""
🔒 <b>Channel Membership Required</b>

হ্যালো {user_name}! 👋

কন্টেন্ট পেতে আপনাকে আমাদের অফিশিয়াল চ্যানেলে জয়েন করতে হবে।
<i>To access content, you must join our official channel.</i>

✅ চ্যানেলে জয়েন করার পর <b>"আমি জয়েন করেছি"</b> বাটনে ক্লিক করুন।

🎬 <b>Official Channel:</b> {config.CHANNEL_USERNAME}
""",
                reply_markup=join_keyboard,
                quote=True
            )
            return
        
        # Step 2: Fetch content from database
        content = await get_content(copy_id)
        
        if not content:
            logger.warning(f"⚠️ Content not found: {copy_id}")
            await message.reply_text(
                "❌ দুঃখিত, এই কন্টেন্ট খুঁজে পাওয়া যায়নি।\n\n"
                "<i>Sorry, this content was not found.</i>\n\n"
                "অনুগ্রহ করে সঠিক লিংক ব্যবহার করুন বা Mini App থেকে আবার চেষ্টা করুন।",
                quote=True
            )
            return
        
        # Step 3: Deliver content
        await deliver_content(client, message, content, copy_id)
        
        logger.info(f"✅ Content {copy_id} delivered to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Content request failed: {e}", exc_info=True)
        await message.reply_text(
            "⚠️ কন্টেন্ট ডেলিভারি ব্যর্থ হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।\n\n"
            "<i>Content delivery failed. Please try again.</i>",
            quote=True
        )


# ═══════════════════════════════════════════════════════════════
# CALLBACK QUERIES
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("^check_membership$"))
async def check_membership_callback(client: Client, callback: CallbackQuery):
    """
    Handle "I've Joined" button click
    Re-check membership and proceed if joined
    """
    user_id = callback.from_user.id
    
    try:
        # Re-check membership
        can_proceed, join_keyboard = await check_force_join(client, user_id)
        
        if can_proceed:
            await callback.answer("✅ Verified! You can now access content.", show_alert=True)
            
            # Try to extract copy_id from original message
            # This is a fallback - ideally user should click deep link again
            await callback.message.edit_text(
                "✅ <b>Membership Verified!</b>\n\n"
                "আপনি এখন কন্টেন্ট অ্যাক্সেস করতে পারবেন।\n"
                "<i>You can now access content.</i>\n\n"
                "অনুগ্রহ করে আপনার Mini App থেকে আবার কন্টেন্ট সিলেক্ট করুন।\n"
                "<i>Please select your content from the Mini App again.</i>"
            )
        else:
            await callback.answer(
                "❌ আপনি এখনও সব চ্যানেলে জয়েন করেননি। অনুগ্রহ করে প্রথমে জয়েন করুন।",
                show_alert=True
            )
            
            # Update keyboard with current status
            await callback.message.edit_reply_markup(reply_markup=join_keyboard)
    
    except Exception as e:
        logger.error(f"❌ Membership check callback failed: {e}")
        await callback.answer("⚠️ Error checking membership. Please try again.", show_alert=True)


@Client.on_callback_query(filters.regex("^how_to_use$"))
async def how_to_use_callback(client: Client, callback: CallbackQuery):
    """Show how to use instructions"""
    help_text = """
📖 <b>কিভাবে ব্যবহার করবেন</b>

1️⃣ আমাদের অফিশিয়াল চ্যানেলে জয়েন করুন
2️⃣ Mini App খুলুন (Google Sheets থেকে)
3️⃣ আপনার পছন্দের কন্টেন্ট সিলেক্ট করুন
4️⃣ "Open in Bot" বাটনে ক্লিক করুন
5️⃣ বট স্বয়ংক্রিয়ভাবে কন্টেন্ট পাঠাবে

━━━━━━━━━━━━━━━━
<b>📖 How to Use</b>

1️⃣ Join our official channel
2️⃣ Open the Mini App (from Google Sheets)
3️⃣ Select your preferred content
4️⃣ Click "Open in Bot" button
5️⃣ Bot will automatically send the content

🎬 <b>Official Channel:</b> {channel}

💡 <b>Tips:</b>
• Videos সরাসরি Telegram এ দেখতে পারবেন
• Forwarding disabled থাকবে (Privacy & Security)
• একই কন্টেন্ট বারবার রিকোয়েস্ট করলে নতুন করে পাঠানো হবে
""".format(channel=config.CHANNEL_USERNAME)
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_help_keyboard()
    )


@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client: Client, callback: CallbackQuery):
    """Show about information"""
    about_text = """
ℹ️ <b>About CineFlix Bot</b>

🎬 CineFlix একটি প্রিমিয়াম কন্টেন্ট ডিস্ট্রিবিউশন সিস্টেম যা Telegram Mini App এর সাথে integrated।

<b>🌟 Features:</b>
✅ HD Quality Video Streaming
✅ Secure Content Delivery
✅ Anti-Duplicate System
✅ Fast & Reliable
✅ Protected Content (No Forwarding)

<b>🔧 Technology:</b>
• Pyrogram Framework
• MongoDB Database
• Railway Hosting
• Google Sheets Integration

<b>👨‍💼 Admin:</b> User ID {admin_id}

<b>📢 Official Channel:</b> {channel}

━━━━━━━━━━━━━━━━
<i>Built with ❤️ for premium content distribution</i>
""".format(admin_id=config.ADMIN_ID, channel=config.CHANNEL_USERNAME)
    
    await callback.message.edit_text(
        about_text,
        reply_markup=get_help_keyboard()
    )


@Client.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_callback(client: Client, callback: CallbackQuery):
    """Go back to welcome message"""
    await callback.message.edit_text(
        config.WELCOME_MESSAGE,
        reply_markup=get_start_keyboard()
    )
