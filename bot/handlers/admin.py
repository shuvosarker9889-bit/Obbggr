# -*- coding: utf-8 -*-
"""
👨‍💼 Admin Panel Handler
Complete admin control panel with all features
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from bot.config import config
from bot.keyboards import (
    get_admin_keyboard,
    get_channel_management_keyboard,
    get_back_keyboard,
    get_close_keyboard
)
from bot.database import (
    get_stats,
    add_extra_channel,
    remove_extra_channel,
    get_extra_channels,
    save_content
)
from bot.utils.duplicate import get_duplicate_stats
import uuid

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == config.ADMIN_ID


# ═══════════════════════════════════════════════════════════════
# ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("admin") & filters.private)
async def admin_panel(client: Client, message: Message):
    """
    Main admin panel command
    Only accessible by admin
    """
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ You are not authorized to use this command.")
        return
    
    admin_text = """
👨‍💼 <b>Admin Control Panel</b>

Welcome to the CineFlix Bot Admin Panel!

━━━━━━━━━━━━━━━━
<b>🔧 Available Features:</b>

📊 <b>Statistics</b> - View bot usage stats
📢 <b>Channels</b> - Manage force join channels
📝 <b>Test Content</b> - Test content delivery
🔄 <b>Refresh DB</b> - Check database status

━━━━━━━━━━━━━━━━
<b>💡 Quick Commands:</b>

/stats - View statistics
/addchannel - Add force join channel
/removechannel - Remove channel
/testcontent - Test content system
/broadcast - Send broadcast message (coming soon)

━━━━━━━━━━━━━━━━
Choose an option below:
"""
    
    await message.reply_text(
        admin_text,
        reply_markup=get_admin_keyboard()
    )


@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    """Show bot statistics"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized access.")
        return
    
    await show_statistics(client, message)


async def show_statistics(client: Client, message: Message, edit: bool = False):
    """
    Display bot statistics
    Can be used for both new messages and edits
    """
    try:
        # Get general stats
        stats = await get_stats()
        
        # Get duplicate prevention stats
        dup_stats = await get_duplicate_stats()
        
        stats_text = f"""
📊 <b>Bot Statistics</b>

━━━━━━━━━━━━━━━━
<b>📦 Content:</b>
📹 Total Videos: {stats.get('total_videos', 0)}
🔗 Total Links: {stats.get('total_links', 0)}
📚 Total Contents: {stats.get('total_contents', 0)}

<b>👥 Users:</b>
👤 Unique Users: {stats.get('unique_users', 0)}
📨 Total Deliveries: {stats.get('total_deliveries', 0)}
📊 Avg per User: {dup_stats.get('avg_deliveries_per_user', 0)}

<b>📢 Channels:</b>
🔒 Main Channel: <code>{config.FORCE_JOIN_CHANNEL_ID}</code>
➕ Extra Channels: {stats.get('extra_channels', 0)}

━━━━━━━━━━━━━━━━
<b>🔧 System Status:</b>
✅ Database: Connected
✅ Bot: Running
✅ Notifications: {'Enabled' if config.ENABLE_NOTIFICATIONS else 'Disabled'}

<i>Last updated: Just now</i>
"""
        
        if edit:
            await message.edit_text(
                stats_text,
                reply_markup=get_back_keyboard()
            )
        else:
            await message.reply_text(
                stats_text,
                reply_markup=get_back_keyboard()
            )
    
    except Exception as e:
        logger.error(f"❌ Failed to show statistics: {e}", exc_info=True)
        error_text = "⚠️ Failed to fetch statistics. Please try again."
        
        if edit:
            await message.edit_text(error_text)
        else:
            await message.reply_text(error_text)


# ═══════════════════════════════════════════════════════════════
# CHANNEL MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("addchannel") & filters.private)
async def add_channel_command(client: Client, message: Message):
    """Add extra force join channel"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized access.")
        return
    
    # Check if channel ID provided
    if len(message.command) < 2:
        await message.reply_text(
            "📢 <b>Add Force Join Channel</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/addchannel CHANNEL_ID</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/addchannel -1001234567890</code>\n\n"
            "💡 <b>Note:</b> Bot must be admin in the channel!"
        )
        return
    
    try:
        channel_id = int(message.command[1])
        
        # Verify bot has access
        try:
            chat = await client.get_chat(channel_id)
            channel_name = chat.title
            
            # Add to database
            success = await add_extra_channel(channel_id, channel_name)
            
            if success:
                await message.reply_text(
                    f"✅ <b>Channel Added Successfully!</b>\n\n"
                    f"📢 <b>Channel:</b> {channel_name}\n"
                    f"🆔 <b>ID:</b> <code>{channel_id}</code>\n\n"
                    f"Users will now be required to join this channel."
                )
                logger.info(f"✅ Admin added channel: {channel_id} ({channel_name})")
            else:
                await message.reply_text("⚠️ Failed to add channel to database.")
        
        except Exception as e:
            await message.reply_text(
                f"❌ <b>Failed to access channel!</b>\n\n"
                f"Make sure:\n"
                f"1. Channel ID is correct\n"
                f"2. Bot is admin in the channel\n"
                f"3. Bot has necessary permissions\n\n"
                f"<code>Error: {str(e)}</code>"
            )
    
    except ValueError:
        await message.reply_text("❌ Invalid channel ID. Must be a number (e.g., -1001234567890)")


@Client.on_message(filters.command("removechannel") & filters.private)
async def remove_channel_command(client: Client, message: Message):
    """Remove extra force join channel"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized access.")
        return
    
    if len(message.command) < 2:
        # Show list of channels
        extra_channels = await get_extra_channels()
        
        if not extra_channels:
            await message.reply_text("📢 No extra channels added.")
            return
        
        channels_text = "📢 <b>Extra Channels:</b>\n\n"
        for ch_id in extra_channels:
            try:
                chat = await client.get_chat(ch_id)
                channels_text += f"• {chat.title} - <code>{ch_id}</code>\n"
            except:
                channels_text += f"• <code>{ch_id}</code>\n"
        
        channels_text += "\n<b>Usage:</b>\n<code>/removechannel CHANNEL_ID</code>"
        
        await message.reply_text(channels_text)
        return
    
    try:
        channel_id = int(message.command[1])
        
        # Remove from database
        success = await remove_extra_channel(channel_id)
        
        if success:
            await message.reply_text(
                f"✅ <b>Channel Removed Successfully!</b>\n\n"
                f"🆔 <b>ID:</b> <code>{channel_id}</code>\n\n"
                f"This channel is no longer required for force join."
            )
            logger.info(f"✅ Admin removed channel: {channel_id}")
        else:
            await message.reply_text("⚠️ Channel not found in database.")
    
    except ValueError:
        await message.reply_text("❌ Invalid channel ID.")


@Client.on_message(filters.command("listchannels") & filters.private)
async def list_channels_command(client: Client, message: Message):
    """List all force join channels"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized access.")
        return
    
    try:
        # Main channel
        main_chat = await client.get_chat(config.FORCE_JOIN_CHANNEL_ID)
        
        channels_text = f"""
📢 <b>Force Join Channels</b>

━━━━━━━━━━━━━━━━
<b>🔒 Main Channel:</b>
• {main_chat.title}
• ID: <code>{config.FORCE_JOIN_CHANNEL_ID}</code>
• Username: {config.CHANNEL_USERNAME}

━━━━━━━━━━━━━━━━
<b>➕ Extra Channels:</b>
"""
        
        # Extra channels
        extra_channels = await get_extra_channels()
        
        if extra_channels:
            for ch_id in extra_channels:
                try:
                    chat = await client.get_chat(ch_id)
                    username = f"@{chat.username}" if chat.username else "Private"
                    channels_text += f"\n• {chat.title}\n  ID: <code>{ch_id}</code>\n  {username}"
                except Exception as e:
                    channels_text += f"\n• <code>{ch_id}</code> (Error: {str(e)[:30]})"
        else:
            channels_text += "\n<i>No extra channels added.</i>"
        
        channels_text += "\n\n━━━━━━━━━━━━━━━━\n"
        channels_text += f"<b>Total:</b> {1 + len(extra_channels)} channel(s)"
        
        await message.reply_text(channels_text)
    
    except Exception as e:
        logger.error(f"❌ Failed to list channels: {e}")
        await message.reply_text("⚠️ Failed to fetch channel list.")


# ═══════════════════════════════════════════════════════════════
# TEST CONTENT
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("testcontent") & filters.private)
async def test_content_command(client: Client, message: Message):
    """Test content delivery system"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized access.")
        return
    
    test_text = """
🧪 <b>Test Content Delivery</b>

<b>Available Tests:</b>

1️⃣ <b>Test Video Delivery</b>
   /testcontent video MESSAGE_ID

2️⃣ <b>Test Link Delivery</b>
   /testcontent link YOUR_URL

3️⃣ <b>Generate Test Copy ID</b>
   /testcontent generate

━━━━━━━━━━━━━━━━
<b>Example:</b>
<code>/testcontent video 123</code>
<code>/testcontent link https://youtube.com/watch?v=xxx</code>
<code>/testcontent generate</code>

💡 <b>Note:</b> Test deliveries will be sent to you (admin).
"""
    
    if len(message.command) < 2:
        await message.reply_text(test_text)
        return
    
    test_type = message.command[1].lower()
    
    if test_type == "generate":
        # Generate test copy_id
        test_copy_id = str(uuid.uuid4())[:8]
        await message.reply_text(
            f"🆔 <b>Test Copy ID Generated:</b>\n\n"
            f"<code>{test_copy_id}</code>\n\n"
            f"You can use this in your Mini App for testing."
        )
    
    elif test_type == "video" and len(message.command) >= 3:
        try:
            msg_id = int(message.command[2])
            test_copy_id = f"test_{uuid.uuid4()[:6]}"
            
            # Save test content
            await save_content(
                copy_id=test_copy_id,
                message_id=msg_id,
                content_type="video"
            )
            
            await message.reply_text(
                f"✅ <b>Test Video Saved!</b>\n\n"
                f"📋 Copy ID: <code>{test_copy_id}</code>\n"
                f"🆔 Message ID: <code>{msg_id}</code>\n\n"
                f"<b>Test Deep Link:</b>\n"
                f"https://t.me/{(await client.get_me()).username}?start=content_{test_copy_id}"
            )
        except ValueError:
            await message.reply_text("❌ Invalid message ID.")
    
    elif test_type == "link" and len(message.command) >= 3:
        test_link = message.command[2]
        test_copy_id = f"test_{uuid.uuid4()[:6]}"
        
        # Save test content
        await save_content(
            copy_id=test_copy_id,
            link=test_link,
            content_type="link"
        )
        
        await message.reply_text(
            f"✅ <b>Test Link Saved!</b>\n\n"
            f"📋 Copy ID: <code>{test_copy_id}</code>\n"
            f"🔗 Link: <code>{test_link}</code>\n\n"
            f"<b>Test Deep Link:</b>\n"
            f"https://t.me/{(await client.get_me()).username}?start=content_{test_copy_id}"
        )
    
    else:
        await message.reply_text(test_text)


# ═══════════════════════════════════════════════════════════════
# CALLBACK QUERIES
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("^admin_"))
async def admin_callbacks(client: Client, callback: CallbackQuery):
    """Handle admin panel callbacks"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    
    action = callback.data.replace("admin_", "")
    
    if action == "stats":
        await show_statistics(client, callback.message, edit=True)
    
    elif action == "channels":
        await callback.message.edit_text(
            "📢 <b>Channel Management</b>\n\n"
            "Manage force join channels here.\n\n"
            "<b>Commands:</b>\n"
            "/addchannel - Add new channel\n"
            "/removechannel - Remove channel\n"
            "/listchannels - List all channels",
            reply_markup=get_channel_management_keyboard()
        )
    
    elif action == "test":
        await callback.message.edit_text(
            "🧪 <b>Test Content System</b>\n\n"
            "Use /testcontent command to test the system.\n\n"
            "See /testcontent for available tests.",
            reply_markup=get_back_keyboard()
        )
    
    elif action == "refresh":
        await callback.answer("🔄 Refreshing database status...", show_alert=False)
        await show_statistics(client, callback.message, edit=True)
    
    elif action == "back":
        await admin_panel(client, callback.message)
    
    elif action == "close":
        await callback.message.delete()
        await callback.answer("✅ Closed")


@Client.on_callback_query(filters.regex("^channel_"))
async def channel_callbacks(client: Client, callback: CallbackQuery):
    """Handle channel management callbacks"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    
    action = callback.data.replace("channel_", "")
    
    if action == "list":
        await list_channels_command(client, callback.message)
    
    elif action == "add":
        await callback.message.edit_text(
            "➕ <b>Add Force Join Channel</b>\n\n"
            "Use this command:\n"
            "<code>/addchannel CHANNEL_ID</code>\n\n"
            "Example:\n"
            "<code>/addchannel -1001234567890</code>",
            reply_markup=get_back_keyboard()
        )
    
    elif action == "remove":
        await callback.message.edit_text(
            "➖ <b>Remove Force Join Channel</b>\n\n"
            "Use this command:\n"
            "<code>/removechannel CHANNEL_ID</code>\n\n"
            "First, use /listchannels to see all channels.",
            reply_markup=get_back_keyboard()
        )
