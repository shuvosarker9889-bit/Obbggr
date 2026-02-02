# -*- coding: utf-8 -*-
"""
CineFlix Bot Package
"""

__version__ = "1.0.0"
__author__ = "CineFlix Team"
__description__ = "Production-ready Telegram content distribution bot"

from bot.config import config
from bot.database import init_database

__all__ = ['config', 'init_database']
