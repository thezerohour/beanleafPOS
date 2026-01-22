/**
 * BeanLeaf POS - Main Bot Application
 * Entry point for the Telegram POS bot
 */

import { Telegraf, session } from 'telegraf';
import * as dotenv from 'dotenv';
import { BotContext } from './types';
import { initDb } from './models/database';
import {
  startCommand,
  browseProducts,
  viewProduct,
  viewCart,
  addToCart,
  clearCart,
  showMainMenu
} from './handlers/customer';
import {
  adminPanel,
  manageProducts,
  showSalesStats,
  editProduct,
  toggleProductAvailability
} from './handlers/admin';
import {
  checkout,
  viewOrderQueue,
  viewOrderDetails,
  completeOrder,
  cancelOrder
} from './handlers/orders';

// Load environment variables
dotenv.config();

// Configure logging
console.log('Starting BeanLeaf POS bot...');

async function main() {
  // Get bot token
  const botToken = process.env.BOT_TOKEN;
  if (!botToken) {
    console.error('BOT_TOKEN not found in environment variables');
    console.error('Please set BOT_TOKEN in your .env file');
    return;
  }

  try {
    // Initialize database
    console.log('Initializing database...');
    await initDb();
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Failed to initialize database:', error);
    console.error('Make sure you have credentials.json in the project root');
    console.error('and GOOGLE_SHEET_ID is set in your .env file');
    return;
  }

  // Create bot
  console.log('Creating bo<BotContext>t application...');
  const bot = new Telegraf(botToken);

  // Enable session support
  bot.use(session());

  // Set up command handlers
  console.log('Setting up handlers...');
  
  // Customer commands
  bot.command('start', startCommand);
  bot.action('browse', browseProducts);
  bot.action(/^product_\d+$/, viewProduct);
  bot.action('cart', viewCart);
  bot.action(/^addcart_\d+$/, addToCart);
  bot.action('cart_clear', clearCart);
  bot.action('main_menu', showMainMenu);
  bot.action('checkout', checkout);

  // Admin commands
  bot.action('admin', adminPanel);
  bot.action('admin_products', manageProducts);
  bot.action('admin_sales', showSalesStats);
  bot.action(/^admin_edit_\d+$/, editProduct);
  bot.action(/^admin_toggle_\d+$/, toggleProductAvailability);
  bot.action('admin_order_queue', viewOrderQueue);

  // Order handlers
  bot.action(/^order_view_\d+$/, viewOrderDetails);
  bot.action(/^order_complete_\d+$/, completeOrder);
  bot.action(/^order_cancel_\d+$/, cancelOrder);

  // Error handling
  bot.catch((err, ctx) => {
    console.error('Bot error:', err);
    ctx.reply('❌ An error occurred. Please try again.');
  });

  // Start bot
  console.log('Starting BeanLeaf POS bot...');
  console.log('Bot is running! Press Ctrl+C to stop.');

  await bot.launch();

  // Enable graceful stop
  process.once('SIGINT', () => {
    console.log('Stopping bot...');
    bot.stop('SIGINT');
  });
  process.once('SIGTERM', () => {
    console.log('Stopping bot...');
    bot.stop('SIGTERM');
  });
}

// Start the application
if (require.main === module) {
  main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export default main;
