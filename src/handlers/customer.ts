/**
 * Customer command handlers
 */

import { Markup } from 'telegraf';
import { BotContext } from '../types';
import { Product } from '../models/product';
import { getMainMenuKeyboard, getProductsKeyboard, getCartKeyboard } from '../utils/keyboards';
import { getOrCreateUser } from '../utils/helpers';

/**
 * Handle /start command
 */
export async function startCommand(ctx: BotContext) {
  try {
    const user = await getOrCreateUser(ctx);
    
    const welcomeMessage = 
      `👋 Welcome to BeanLeaf POS, ${user.fullName}!\n\n` +
      `🛍️ Browse our products and place orders easily.\n\n` +
      `Use the menu below to get started:`;
    
    await ctx.reply(welcomeMessage, getMainMenuKeyboard(user.is_admin));
  } catch (error) {
    console.error('Error in start command:', error);
    await ctx.reply('❌ An error occurred. Please try again.');
  }
}

/**
 * Browse available products
 */
export async function browseProducts(ctx: BotContext) {
  try {
    const products = await Product.getAll(true);
    
    if (products.length === 0) {
      const message = '❌ No products available at the moment.';
      const keyboard = Markup.inlineKeyboard([
        [Markup.button.callback('🏠 Main Menu', 'main_menu')]
      ]);
      
      if (ctx.callbackQuery) {
        await ctx.editMessageText(message, keyboard);
      } else {
        await ctx.reply(message, keyboard);
      }
      return;
    }
    
    const message = '🛍️ *Available Products*\n\n';
    const keyboard = getProductsKeyboard(products);
    
    if (ctx.callbackQuery) {
      await ctx.editMessageText(message, { 
        parse_mode: 'Markdown',
        ...keyboard 
      });
    } else {
      await ctx.reply(message, { 
        parse_mode: 'Markdown',
        ...keyboard 
      });
    }
  } catch (error) {
    console.error('Error browsing products:', error);
    const errorMsg = '❌ Error loading products. Please try again.';
    
    if (ctx.callbackQuery) {
      await ctx.answerCbQuery(errorMsg, { show_alert: true });
    } else {
      await ctx.reply(errorMsg);
    }
  }
}

/**
 * View product details
 */
export async function viewProduct(ctx: BotContext) {
  if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return;
  
  await ctx.answerCbQuery();
  
  const productId = parseInt(ctx.callbackQuery.data.split('_')[1]);
  
  try {
    const product = await Product.getById(productId);
    
    if (!product) {
      await ctx.editMessageText('❌ Product not found.');
      return;
    }
    
    let message = `🏷️ *${product.name}*\n\n`;
    message += `💰 Price: $${product.price.toFixed(2)}\n`;
    
    if (product.description) {
      message += `📝 ${product.description}\n`;
    }
    
    message += `\n📦 Stock: ${product.stock} available\n`;
    
    // Show cart quantity if any
    const cart = ctx.session?.cart || {};
    const cartQty = cart[product.id!] || 0;
    if (cartQty) {
      message += `🛒 In your cart: ${cartQty}\n`;
    }
    
    const keyboard = Markup.inlineKeyboard([
      [Markup.button.callback('➕ Add to Cart', `addcart_${productId}`)],
      [Markup.button.callback('◀️ Back to Products', 'browse')],
      [Markup.button.callback('🏠 Main Menu', 'main_menu')]
    ]);
    
    try {
      await ctx.editMessageText(message, {
        parse_mode: 'Markdown',
        ...keyboard
      });
    } catch (error: any) {
      // Ignore "message is not modified" errors
      if (!error.description?.includes('message is not modified')) {
        throw error;
      }
    }
  } catch (error) {
    console.error('Error viewing product:', error);
    await ctx.answerCbQuery('❌ Error loading product.', { show_alert: true });
  }
}

/**
 * View shopping cart
 */
export async function viewCart(ctx: BotContext) {
  if (ctx.callbackQuery) {
    await ctx.answerCbQuery();
  }
  
  const cart = ctx.session?.cart || {};
  
  if (Object.keys(cart).length === 0) {
    const message = '🛒 Your cart is empty.\n\nBrowse products to add items!';
    const keyboard = Markup.inlineKeyboard([
      [Markup.button.callback('🛍️ Browse Products', 'browse')],
      [Markup.button.callback('🏠 Main Menu', 'main_menu')]
    ]);
    
    if (ctx.callbackQuery) {
      await ctx.editMessageText(message, keyboard);
    } else {
      await ctx.reply(message, keyboard);
    }
    return;
  }
  
  try {
    let message = '🛒 *Your Shopping Cart*\n\n';
    let total = 0;
    
    for (const [productIdStr, quantity] of Object.entries(cart)) {
      const productId = parseInt(productIdStr);
      const product = await Product.getById(productId);
      
      if (product) {
        const subtotal = product.price * (quantity as number);
        total += subtotal;
        message += `• ${product.name}\n`;
        message += `  ${quantity} x $${product.price.toFixed(2)} = $${subtotal.toFixed(2)}\n\n`;
      }
    }
    
    message += `*Total: $${total.toFixed(2)}*`;
    
    const keyboard = getCartKeyboard(true);
    
    if (ctx.callbackQuery) {
      await ctx.editMessageText(message, {
        parse_mode: 'Markdown',
        ...keyboard
      });
    } else {
      await ctx.reply(message, {
        parse_mode: 'Markdown',
        ...keyboard
      });
    }
  } catch (error) {
    console.error('Error viewing cart:', error);
    await ctx.reply('❌ Error loading cart. Please try again.');
  }
}

/**
 * Add item to cart
 */
export async function addToCart(ctx: BotContext) {
  if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return;
  
  const productId = parseInt(ctx.callbackQuery.data.split('_')[1]);
  
  try {
    const product = await Product.getById(productId);
    
    if (!product) {
      await ctx.answerCbQuery('❌ Product not found!', { show_alert: true });
      return;
    }
    
    if (product.stock === 0) {
      await ctx.answerCbQuery('❌ Product out of stock!', { show_alert: true });
      return;
    }
    
    // Initialize session cart if not exists
    if (!ctx.session) {
      ctx.session = { cart: {} };
    }
    
    if (!ctx.session.cart) {
      ctx.session.cart = {};
    }
    
    const cart = ctx.session.cart;
    const currentQty = cart[productId] || 0;
    
    if (currentQty >= product.stock) {
      await ctx.answerCbQuery('❌ Cannot add more than available stock!', { show_alert: true });
      return;
    }
    
    cart[productId] = currentQty + 1;
    
    await ctx.answerCbQuery(`✅ Added ${product.name} to cart!`);
    
    // Update the product view to show new cart quantity
    await viewProduct(ctx);
  } catch (error) {
    console.error('Error adding to cart:', error);
    await ctx.answerCbQuery('❌ Error adding to cart.', { show_alert: true });
  }
}

/**
 * Clear cart
 */
export async function clearCart(ctx: BotContext) {
  if (ctx.callbackQuery) {
    await ctx.answerCbQuery();
  }
  
  if (ctx.session?.cart) {
    ctx.session.cart = {};
  }
  
  await ctx.reply('🗑️ Cart cleared!', getMainMenuKeyboard(false));
}

/**
 * Show main menu
 */
export async function showMainMenu(ctx: BotContext) {
  if (ctx.callbackQuery) {
    await ctx.answerCbQuery();
  }
  
  try {
    const user = await getOrCreateUser(ctx);
    const message = '🏠 *Main Menu*\n\nWhat would you like to do?';
    
    if (ctx.callbackQuery) {
      await ctx.editMessageText(message, {
        parse_mode: 'Markdown',
        ...getMainMenuKeyboard(user.is_admin)
      });
    } else {
      await ctx.reply(message, {
        parse_mode: 'Markdown',
        ...getMainMenuKeyboard(user.is_admin)
      });
    }
  } catch (error) {
    console.error('Error showing main menu:', error);
    await ctx.reply('❌ Error loading menu. Please try /start again.');
  }
}
