/**
 * Order processing handlers
 */

import { Markup } from 'telegraf';
import { BotContext } from '../types';
import { Order, OrderItem } from '../models/order';
import { Product } from '../models/product';
import { getOrCreateUser } from '../utils/helpers';

/**
 * Process checkout
 */
export async function checkout(ctx: BotContext) {
  if (!ctx.callbackQuery) return;
  
  await ctx.answerCbQuery();
  
  const cart = ctx.session?.cart || {};
  
  if (Object.keys(cart).length === 0) {
    await ctx.answerCbQuery('❌ Your cart is empty!', { show_alert: true });
    return;
  }
  
  try {
    const user = await getOrCreateUser(ctx);
    
    // Calculate total and validate stock
    let totalAmount = 0;
    const orderItems: any[] = [];
    
    for (const [productIdStr, quantity] of Object.entries(cart)) {
      const productId = parseInt(productIdStr);
      const product = await Product.getById(productId);
      
      if (!product) {
        await ctx.answerCbQuery('❌ Product not found!', { show_alert: true });
        return;
      }
      
      if (product.stock < (quantity as number)) {
        await ctx.answerCbQuery(
          `❌ Not enough stock for ${product.name}. Available: ${product.stock}`,
          { show_alert: true }
        );
        return;
      }
      
      const subtotal = product.price * (quantity as number);
      totalAmount += subtotal;
      
      orderItems.push({
        product,
        quantity: quantity as number,
        subtotal
      });
    }
    
    // Create order as pending
    const order = new Order({
      user_id: user.id!,
      total_amount: totalAmount,
      status: 'pending'
    });
    await order.save();
    
    // Create order items
    for (const item of orderItems) {
      const orderItem = new OrderItem({
        order_id: order.id!,
        product_id: item.product.id!,
        product_name: item.product.name,
        quantity: item.quantity,
        price: item.product.price,
        subtotal: item.subtotal
      });
      await orderItem.save();
    }
    
    // Clear cart
    if (ctx.session) {
      ctx.session.cart = {};
    }
    
    // Build confirmation message
    const lines = [
      '✅ Order placed!',
      'Status: Pending store confirmation',
      `Order ID: #${order.id}`,
      `Total: $${totalAmount.toFixed(2)}`,
      '\nItems:'
    ];
    
    for (const item of orderItems) {
      lines.push(
        `• ${item.product.name} — ${item.quantity} x $${item.product.price.toFixed(2)} = $${item.subtotal.toFixed(2)}`
      );
    }
    
    const message = lines.join('\n');
    
    const keyboard = Markup.inlineKeyboard([
      [Markup.button.callback('🛍️ Shop Again', 'browse')],
      [Markup.button.callback('🏠 Main Menu', 'main_menu')]
    ]);
    
    await ctx.editMessageText(message, keyboard);
  } catch (error) {
    console.error('Error during checkout:', error);
    await ctx.answerCbQuery('❌ Error processing order. Please try again.', { show_alert: true });
  }
}

/**
 * View order queue (for admins)
 */
export async function viewOrderQueue(ctx: BotContext) {
  if (!ctx.callbackQuery) return;
  
  await ctx.answerCbQuery();
  
  try {
    const user = await getOrCreateUser(ctx);
    
    if (!user.is_admin) {
      await ctx.answerCbQuery('❌ Admin access required!', { show_alert: true });
      return;
    }
    
    const pendingOrders = await Order.getAllPending();
    
    if (pendingOrders.length === 0) {
      const message = '📥 *Order Queue*\n\nNo pending orders.';
      const keyboard = Markup.inlineKeyboard([
        [Markup.button.callback('◀️ Back to Admin', 'admin')]
      ]);
      
      await ctx.editMessageText(message, {
        parse_mode: 'Markdown',
        ...keyboard
      });
      return;
    }
    
    let message = `📥 *Order Queue* (${pendingOrders.length} orders)\n\n`;
    
    const buttons = [];
    for (const order of pendingOrders) {
      buttons.push([
        Markup.button.callback(
          `Order #${order.id} - $${order.total_amount.toFixed(2)} (${order.status})`,
          `order_view_${order.id}`
        )
      ]);
    }
    
    buttons.push([Markup.button.callback('◀️ Back to Admin', 'admin')]);
    
    const keyboard = Markup.inlineKeyboard(buttons);
    
    await ctx.editMessageText(message, {
      parse_mode: 'Markdown',
      ...keyboard
    });
  } catch (error) {
    console.error('Error viewing order queue:', error);
    await ctx.answerCbQuery('❌ Error loading orders.', { show_alert: true });
  }
}

/**
 * View order details
 */
export async function viewOrderDetails(ctx: BotContext) {
  if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return;
  
  await ctx.answerCbQuery();
  
  const orderId = parseInt(ctx.callbackQuery.data.split('_')[2]);
  
  try {
    const order = await Order.getById(orderId);
    
    if (!order) {
      await ctx.editMessageText('❌ Order not found.');
      return;
    }
    
    await order.getItems();
    
    let message = `📋 *Order #${order.id}*\n\n`;
    message += `Status: ${order.status}\n`;
    message += `Total: $${order.total_amount.toFixed(2)}\n\n`;
    message += `Items:\n`;
    
    for (const item of order.items) {
      message += `• ${item.product_name} x${item.quantity} - $${item.subtotal.toFixed(2)}\n`;
    }
    
    const keyboard = Markup.inlineKeyboard([
      [
        Markup.button.callback('✅ Complete', `order_complete_${orderId}`),
        Markup.button.callback('❌ Cancel', `order_cancel_${orderId}`)
      ],
      [Markup.button.callback('◀️ Back to Queue', 'admin_order_queue')]
    ]);
    
    await ctx.editMessageText(message, {
      parse_mode: 'Markdown',
      ...keyboard
    });
  } catch (error) {
    console.error('Error viewing order details:', error);
    await ctx.answerCbQuery('❌ Error loading order.', { show_alert: true });
  }
}

/**
 * Complete an order
 */
export async function completeOrder(ctx: BotContext) {
  if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return;
  
  const orderId = parseInt(ctx.callbackQuery.data.split('_')[2]);
  
  try {
    const order = await Order.getById(orderId);
    
    if (!order) {
      await ctx.answerCbQuery('❌ Order not found!', { show_alert: true });
      return;
    }
    
    // Update order status
    order.status = 'completed';
    order.completed_at = new Date().toISOString();
    await order.save();
    
    // Decrement stock for each item
    await order.getItems();
    for (const item of order.items) {
      const product = await Product.getById(item.product_id);
      if (product) {
        product.stock = Math.max(0, product.stock - item.quantity);
        await product.save();
      }
    }
    
    await ctx.answerCbQuery('✅ Order completed!');
    
    // Redirect back to queue
    await viewOrderQueue(ctx);
  } catch (error) {
    console.error('Error completing order:', error);
    await ctx.answerCbQuery('❌ Error completing order.', { show_alert: true });
  }
}

/**
 * Cancel an order
 */
export async function cancelOrder(ctx: BotContext) {
  if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return;
  
  const orderId = parseInt(ctx.callbackQuery.data.split('_')[2]);
  
  try {
    const order = await Order.getById(orderId);
    
    if (!order) {
      await ctx.answerCbQuery('❌ Order not found!', { show_alert: true });
      return;
    }
    
    order.status = 'cancelled';
    await order.save();
    
    await ctx.answerCbQuery('❌ Order cancelled.');
    
    // Redirect back to queue
    await viewOrderQueue(ctx);
  } catch (error) {
    console.error('Error cancelling order:', error);
    await ctx.answerCbQuery('❌ Error cancelling order.', { show_alert: true });
  }
}
