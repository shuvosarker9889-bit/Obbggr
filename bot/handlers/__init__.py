# -*- coding: utf-8 -*-
"""
Handler Registration
Registers all bot handlers
"""

import logging
from pyrogram import Client

logger = logging.getLogger(__name__)


def register_handlers(app: Client):
    """
    Register all handlers to the bot
    Import handlers here to avoid circular imports
    """
    try:
        # Import all handler modules
        from bot.handlers import start, content, admin
        
        logger.info("✅ All handlers registered successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to register handlers: {e}", exc_info=True)
        raise


__all__ = ['register_handlers']
