# -*- coding: utf-8 -*-
"""
⌨️ Inline Keyboards
All bot keyboards in one place
"""

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import config


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Welcome screen keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Official Channel", url=f"https://t.me/{config.CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("📖 How to Use", callback_data="how_to_use")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ])


def get_link_keyboard(link: str, button_text: str = "🔗 Open Link") -> InlineKeyboardMarkup:
    """Keyboard for link content"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(button_text, url=link)]
    ])


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin panel main menu"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
            InlineKeyboardButton("📢 Channels", callback_data="admin_channels")
        ],
        [
            InlineKeyboardButton("📝 Test Content", callback_data="admin_test"),
            InlineKeyboardButton("🔄 Refresh DB", callback_data="admin_refresh")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="admin_close")]
    ])


def get_channel_management_keyboard() -> InlineKeyboardMarkup:
    """Channel management keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Channel", callback_data="channel_add"),
            InlineKeyboardButton("➖ Remove Channel", callback_data="channel_remove")
        ],
        [
            InlineKeyboardButton("📋 List Channels", callback_data="channel_list"),
            InlineKeyboardButton("🔙 Back", callback_data="admin_back")
        ]
    ])


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Simple back button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="admin_back")]
    ])


def get_close_keyboard() -> InlineKeyboardMarkup:
    """Simple close button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Close", callback_data="admin_close")]
    ])


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Help section keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{config.CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])
