"""
BeanLeaf POS - Main Bot Application
"""

import os
import sys
import logging
from pathlib import Path

# Add the bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from telegram.ext import Application
from dotenv import load_dotenv

from models import init_db
from handlers import setup_customer_handlers, setup_admin_handlers, setup_order_handlers

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
        return
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    
    # Create application
    logger.info("Creating bot application...")
    application = Application.builder().token(bot_token).build()
    
    # Set up handlers
    logger.info("Setting up handlers...")
    setup_customer_handlers(application)
    setup_admin_handlers(application)
    setup_order_handlers(application)
    
    # Start bot
    logger.info("Starting BeanLeaf POS bot...")
    logger.info("Bot is running! Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == '__main__':
    main()
