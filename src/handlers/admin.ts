/**
 * Admin command handlers
 */

import { Markup } from 'telegraf';
import { BotContext } from '../types';
import { Product } from '../models/product';
import { Order } from '../models/order';
import { getOrCreateUser } from '../utils/helpers';
import { getAdminKeyboard } from '../utils/keyboards';

/**
 * Show admin panel
 */
export async function adminPanel(ctx: BotContext) {
  if (ctx.callbackQuery) {
    await ctx.answerCbQuery();
  }
  
  try {
    const user = await getOrCreateUser(ctx);
    
    if (!user.is_admin) {
      const message = "❌ You don't have admin access.";
      if (ctx.callbackQuery) {
        await ctx.answerCbQuery(message, { show_alert: true });
      } else {
        await ctx.reply(message);
      }
      return;
    }
    
    const message = '🔧 *Admin Panel*\n\nManage your POS system:';
    
    if (ctx.callbackQuery) {
      await ctx.editMessageText(message, {
        parse_mode: 'Markdown',
        ...getAdminKeyboard()
      });
    } else {
      await ctx.reply(message, {
        parse_mode: 'Markdown',
        ...getAdminKeyboard()
      });
    }
  } catch (error) {
    console.error('Error in admin panel:', error);
    if (ctx.callbackQuery) {
      await ctx.answerCbQuery('❌ Error loading admin panel.', { show_alert: true });
    }
  }
}

/**
 * Manage products
 */
export async function manageProducts(ctx: BotContext) {
  if (!ctx.callbackQuery) return;
  
  await ctx.answerCbQuery();
  
  try {
    const products = await Product.getAll();
    
    if (products.length === 0) {
      const message = '📦 No products found.\n\nAdd your first product!';
      const keyboard = Markup.inlineKeyboard([
        [Markup.button.callback('➕ Add Product', 'admin_add_product')],
        [Markup.button.callback('◀️ Back', 'admin')]
      ]);
      
      await ctx.editMessageText(message, keyboard);
      return;
    }
    
    const message = '📦 *Product Management*\n\n';
    
    const buttons = [];
    for (const product of products) {
      const status = product.is_available ? '✅' : '❌';
      buttons.push([
        Markup.button.callback(
          `${status} ${product.name} - $${product.price.toFixed(2)} (Stock: ${product.stock})`,
          `admin_edit_${product.id}`
        )
      ]);
    }
    
    buttons.push([Markup.button.callback('➕ Add Product', 'admin_add_product')]);
    buttons.push([Markup.button.callback('◀️ Back', 'admin')]);
    
    const keyboard = Markup.inlineKeyboard(buttons);
    
    await ctx.editMessageText(message, {
      parse_mode: 'Markdown',
      ...keyboard
    });
  } catch (error) {
    console.error('Error managing products:', error);
    await ctx.answerCbQuery('❌ Error loading products.', { show_alert: true });
  }
}

/**
 * Show sales statistics
 */
export async function showSalesStats(ctx: BotContext) {
  if (!ctx.callbackQuery) return;
  
  await ctx.answerCbQuery();
  
  try {
    const completedOrders = await Order.getAllCompleted();
    
    let totalRevenue = 0;
    let totalOrders = completedOrders.length;
    
    for (const order of completedOrders) {
      totalRevenue += order.total_amount;
    }
    
    const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;
    
    let message = '📊 *Sales Statistics*\n\n';
    message += `Total Orders: ${totalOrders}\n`;
    message += `Total Revenue: $${totalRevenue.toFixed(2)}\n`;
    message += `Average Order: $${avgOrderValue.toFixed(2)}\n`;
    
    const keyboard = Markup.inlineKeyboard([
      [Markup.button.callback('◀️ Back to Admin', 'admin')]
    ]);
    
    await ctx.editMessageText(message, {
      parse_mode: 'Markdown',
      ...keyboard
    });
  } catch (error) {
    console.error('Error showing sales stats:', error);
    await ctx.answerCbQuery('❌ Error loading statistics.', { show_alert: true });
  }
}

/**
 * Edit product (placeholder - would need conversation handler)
 */
export async function editProduct(ctx: BotContext) {
  if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return;
  
  await ctx.answerCbQuery();
  
  const productId = parseInt(ctx.callbackQuery.data.split('_')[2]);
  
  try {
    const product = await Product.getById(productId);
    
    if (!product) {
      await ctx.editMessageText('❌ Product not found.');
      return;
    }
    
    let message = `📦 *Edit Product*\n\n`;
    message += `Name: ${product.name}\n`;
    message += `Price: $${product.price.toFixed(2)}\n`;
    message += `Stock: ${product.stock}\n`;
    message += `Available: ${product.is_available ? 'Yes' : 'No'}\n`;
    
    const keyboard = Markup.inlineKeyboard([
      [
        Markup.button.callback('Toggle Availability', `admin_toggle_${productId}`),
        Markup.button.callback('Delete', `admin_delete_${productId}`)
      ],
      [Markup.button.callback('◀️ Back to Products', 'admin_products')]
    ]);
    
    await ctx.editMessageText(message, {
      parse_mode: 'Markdown',
      ...keyboard
    });
  } catch (error) {
    console.error('Error editing product:', error);
    await ctx.answerCbQuery('❌ Error loading product.', { show_alert: true });
  }
}

/**
 * Toggle product availability
 */
export async function toggleProductAvailability(ctx: BotContext) {
  if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return;
  
  const productId = parseInt(ctx.callbackQuery.data.split('_')[2]);
  
  try {
    const product = await Product.getById(productId);
    
    if (!product) {
      await ctx.answerCbQuery('❌ Product not found!', { show_alert: true });
      return;
    }
    
    product.is_available = !product.is_available;
    await product.save();
    
    await ctx.answerCbQuery(`✅ Product ${product.is_available ? 'enabled' : 'disabled'}`);
    
    // Refresh the edit view
    await editProduct(ctx);
  } catch (error) {
    console.error('Error toggling product:', error);
    await ctx.answerCbQuery('❌ Error updating product.', { show_alert: true });
  }
}
