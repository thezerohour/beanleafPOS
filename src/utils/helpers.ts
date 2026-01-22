/**
 * Helper utility functions
 */

import { BotContext } from '../types';
import { User } from '../models/user';

/**
 * Get or create a user from Telegram context
 */
export async function getOrCreateUser(ctx: BotContext): Promise<User> {
  if (!ctx.from) {
    throw new Error('No user information available');
  }

  const telegramId = ctx.from.id;
  let user = await User.getByTelegramId(telegramId);

  if (!user) {
    user = new User({
      telegram_id: telegramId,
      username: ctx.from.username,
      first_name: ctx.from.first_name,
      last_name: ctx.from.last_name,
      is_admin: false
    });
    await user.save();
  }

  return user;
}

/**
 * Format price for display
 */
export function formatPrice(price: number): string {
  return `$${price.toFixed(2)}`;
}

/**
 * Format date for display
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString();
}

/**
 * Check if user is admin
 */
export async function isAdmin(ctx: BotContext): Promise<boolean> {
  try {
    const user = await getOrCreateUser(ctx);
    return user.is_admin;
  } catch {
    return false;
  }
}
