#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 CineFlix Content Distribution Bot
Main Entry Point - Production Ready
Created for: @Cinaflix_Streembot
"""

import asyncio
import logging
from pyrogram import Client
from bot.config import config
from bot.database import init_database
from bot.handlers import register_handlers

# Configure logging - বাংলায় error দেখাবে
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """
    Main bot initialization and startup
    Database connect করে bot চালু করে
    """
    try:
        # Database connection
        logger.info("🔄 Connecting to MongoDB...")
        await init_database()
        logger.info("✅ Database connected successfully!")
        
        # Initialize bot
        app = Client(
            "cineflix_bot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            workers=4,  # Multiple workers for better performance
            sleep_threshold=60  # Flood wait handling
        )
        
        # Register all handlers
        register_handlers(app)
        
        logger.info("🚀 Starting CineFlix Bot...")
        logger.info(f"👤 Admin ID: {config.ADMIN_ID}")
        logger.info(f"📺 Content Channel: {config.CONTENT_CHANNEL_ID}")
        logger.info(f"🔒 Force Join Channel: {config.FORCE_JOIN_CHANNEL_ID}")
        
        # Start the bot
        await app.start()
        logger.info("✅ Bot started successfully! Ready to serve content! 🎬")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("⚠️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}", exc_info=True)
        raise
    finally:
        try:
            await app.stop()
            logger.info("👋 Bot stopped gracefully")
        except:
            pass


if __name__ == "__main__":
    # Windows compatibility
    if asyncio.get_event_loop_policy().__class__.__name__ == 'WindowsProactorEventLoopPolicy':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
