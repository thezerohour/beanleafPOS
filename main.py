#!/usr/bin/env python
"""
BeanLeaf POS - Main Bot Application
Entry point for the Telegram POS bot
"""

import os
import sys
import logging
from telegram.error import BadRequest

# Ensure bot is importable
sys.path.insert(0, os.path.dirname(__file__))

from telegram.ext import Application
from dotenv import load_dotenv

from bot.models import init_db
from bot.handlers import setup_customer_handlers, setup_admin_handlers, setup_order_handlers

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot"""
    # Get bot token
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        logger.error("Please set BOT_TOKEN in your .env file")
        return
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.error("Make sure you have credentials.json in the project root")
        logger.error("and GOOGLE_SHEET_ID is set in your .env file")
        return
    
    try:
        # Create application
        logger.info("Creating bot application...")
        application = Application.builder().token(bot_token).build()
        
        # Error handler to avoid unhandled exceptions
        async def error_handler(update, context):
            logger.error("Unhandled error", exc_info=context.error)
            try:
                if update and update.effective_message:
                    await update.effective_message.reply_text("❌ Something went wrong. Please try again.")
            except BadRequest:
                # Message might be deleted/unchanged; ignore
                pass
        application.add_error_handler(error_handler)
        
        # Set up handlers  
        logger.info("Setting up handlers...")
        setup_customer_handlers(application)
        setup_admin_handlers(application)
        setup_order_handlers(application)
        
        # Start bot
        logger.info("Starting BeanLeaf POS bot...")
        logger.info("Bot is running! Press Ctrl+C to stop.")
        
        # Run with simpler polling
        import asyncio
        application.run_polling()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()
