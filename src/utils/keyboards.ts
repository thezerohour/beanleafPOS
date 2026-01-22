/**
 * Keyboard layouts for bot interactions
 */

import { Markup } from 'telegraf';
import { Product } from '../models/product';

/**
 * Get main menu keyboard
 */
export function getMainMenuKeyboard(isAdmin: boolean = false): any {
  const buttons = [
    [Markup.button.callback('🛍️ Browse Products', 'browse')],
    [Markup.button.callback('🛒 View Cart', 'cart')]
  ];

  if (isAdmin) {
    buttons.push([Markup.button.callback('🔧 Admin Panel', 'admin')]);
  }

  return Markup.inlineKeyboard(buttons);
}

/**
 * Get products listing keyboard
 */
export function getProductsKeyboard(products: Product[]): any {
  const buttons = products.map(product => {
    let buttonText = `${product.name} - $${product.price.toFixed(2)}`;
    if (product.stock === 0) {
      buttonText += ' (Out of Stock)';
    }

    return [Markup.button.callback(buttonText, `product_${product.id}`)];
  });

  buttons.push([Markup.button.callback('🏠 Main Menu', 'main_menu')]);

  return Markup.inlineKeyboard(buttons);
}

/**
 * Get admin panel keyboard
 */
export function getAdminKeyboard(): any {
  return Markup.inlineKeyboard([
    [Markup.button.callback('➕ Add Product', 'admin_add_product')],
    [Markup.button.callback('📥 Order Queue', 'admin_order_queue')],
    [Markup.button.callback('📦 Manage Products', 'admin_products')],
    [Markup.button.callback('📊 Sales Statistics', 'admin_sales')],
    [Markup.button.callback('🏠 Main Menu', 'main_menu')]
  ]);
}

/**
 * Get product detail keyboard
 */
export function getProductDetailKeyboard(productId: number, inStock: boolean): any {
  const buttons = [];

  if (inStock) {
    buttons.push([
      Markup.button.callback('➖', `cart_remove_${productId}`),
      Markup.button.callback('Add to Cart', `cart_add_${productId}`),
      Markup.button.callback('➕', `cart_add_more_${productId}`)
    ]);
  }

  buttons.push([Markup.button.callback('⬅️ Back to Products', 'browse')]);
  buttons.push([Markup.button.callback('🏠 Main Menu', 'main_menu')]);

  return Markup.inlineKeyboard(buttons);
}

/**
 * Get cart keyboard
 */
export function getCartKeyboard(hasItems: boolean): any {
  const buttons = [];

  if (hasItems) {
    buttons.push([Markup.button.callback('✅ Checkout', 'checkout')]);
    buttons.push([Markup.button.callback('🗑️ Clear Cart', 'cart_clear')]);
  }

  buttons.push([Markup.button.callback('🛍️ Continue Shopping', 'browse')]);
  buttons.push([Markup.button.callback('🏠 Main Menu', 'main_menu')]);

  return Markup.inlineKeyboard(buttons);
}

/**
 * Get confirmation keyboard
 */
export function getConfirmationKeyboard(action: string): any {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback('✅ Yes', `confirm_${action}`),
      Markup.button.callback('❌ No', `cancel_${action}`)
    ]
  ]);
}
