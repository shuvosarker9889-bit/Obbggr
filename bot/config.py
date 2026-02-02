# -*- coding: utf-8 -*-
"""
🔧 Bot Configuration
All credentials and settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Bot Configuration Class"""
    
    # ═══════════════════════════════════════════════
    # 🤖 TELEGRAM BOT CREDENTIALS
    # ═══════════════════════════════════════════════
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8006015641:AAHX1rE8ppAGsK4fnEmBUnFEr_xoWhfLDc4")
    API_ID = int(os.getenv("API_ID", "25115930"))  # Default Pyrogram API ID
    API_HASH = os.getenv("API_HASH", "11f8f3d058991d44083d5c7c135964c5")  # Default Pyrogram API Hash
    
    # ═══════════════════════════════════════════════
    # 👨‍💼 ADMIN CONFIGURATION
    # ═══════════════════════════════════════════════
    ADMIN_ID = int(os.getenv("ADMIN_ID", "1858324638"))
    
    # ═══════════════════════════════════════════════
    # 📺 CHANNEL CONFIGURATION
    # ═══════════════════════════════════════════════
    CONTENT_CHANNEL_ID = int(os.getenv("CONTENT_CHANNEL_ID", "-1003872857468"))
    FORCE_JOIN_CHANNEL_ID = int(os.getenv("FORCE_JOIN_CHANNEL_ID", "-1003749088877"))
    CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Cineflixofficialbd")
    
    # ═══════════════════════════════════════════════
    # 🗄️ DATABASE CONFIGURATION
    # ═══════════════════════════════════════════════
    MONGODB_URI = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://joymodol717:risha464323@cluster0.i9ueyks.mongodb.net/?appName=Cluster0"
    )
    DATABASE_NAME = os.getenv("DATABASE_NAME", "cineflix_bot")
    
    # ═══════════════════════════════════════════════
    # 🔔 NOTIFICATION SETTINGS
    # ═══════════════════════════════════════════════
    ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "Yes").lower() == "yes"
    
    # ═══════════════════════════════════════════════
    # 💬 WELCOME MESSAGE (Bangla + Professional)
    # ═══════════════════════════════════════════════
    WELCOME_MESSAGE = """
🎬 <b>স্বাগতম CineFlix এ!</b>

আপনাকে আমাদের প্রিমিয়াম কন্টেন্ট ডিস্ট্রিবিউশন বটে স্বাগতম! 

🌟 <b>বিশেষ সুবিধা:</b>
✅ HD Quality Videos
✅ সরাসরি Telegram এ দেখুন
✅ দ্রুত ও নিরাপদ ডেলিভারি
✅ ডাউনলোড সাপোর্ট

📢 <b>কন্টেন্ট পেতে:</b>
আমাদের অফিশিয়াল চ্যানেলে জয়েন করুন এবং Mini App থেকে আপনার পছন্দের কন্টেন্ট সিলেক্ট করুন।

🎯 <b>Official Channel:</b> {}

<i>আপনার বিনোদনের সাথী - CineFlix 🎭</i>
""".format(CHANNEL_USERNAME)
    
    # ═══════════════════════════════════════════════
    # 🛡️ SECURITY SETTINGS
    # ═══════════════════════════════════════════════
    PROTECT_CONTENT = True  # Video forwarding disabled
    MAX_RETRIES = 3  # Database reconnection attempts
    FLOOD_WAIT_TOLERANCE = 60  # Seconds to wait on flood
    
    # ═══════════════════════════════════════════════
    # 📝 LOGGING
    # ═══════════════════════════════════════════════
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate all required configurations"""
        required = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "ADMIN_ID": cls.ADMIN_ID,
            "CONTENT_CHANNEL_ID": cls.CONTENT_CHANNEL_ID,
            "FORCE_JOIN_CHANNEL_ID": cls.FORCE_JOIN_CHANNEL_ID,
            "MONGODB_URI": cls.MONGODB_URI
        }
        
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        
        return True


# Global config instance
config = Config()

# Validate on import
config.validate()
