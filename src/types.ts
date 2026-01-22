/**
 * Type definitions for bot context
 */

import { Context as TelegrafContext } from 'telegraf';
import { Update } from 'telegraf/types';

export interface SessionData {
  cart: Record<number, number>;
}

export interface BotContext extends TelegrafContext<Update> {
  session?: SessionData;
}
