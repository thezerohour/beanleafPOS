/**
 * User model
 */

import { addRecord, updateRecord, findRecord } from './database';

export interface IUser {
  id?: number;
  telegram_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  is_admin?: boolean | string;
  created_at?: string;
}

export class User {
  id?: number;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  created_at: string;

  constructor(data: IUser) {
    this.id = data.id ? parseInt(String(data.id)) : undefined;
    this.telegram_id = parseInt(String(data.telegram_id));
    this.username = String(data.username || '');
    this.first_name = String(data.first_name || '');
    this.last_name = String(data.last_name || '');
    
    // Handle boolean conversion for is_admin
    if (typeof data.is_admin === 'string') {
      this.is_admin = data.is_admin.toLowerCase() === 'true';
    } else {
      this.is_admin = Boolean(data.is_admin);
    }
    
    this.created_at = data.created_at || new Date().toISOString();
  }

  /**
   * Save user to Google Sheets
   */
  async save(): Promise<User> {
    const data = {
      telegram_id: this.telegram_id,
      username: this.username,
      first_name: this.first_name,
      last_name: this.last_name,
      is_admin: String(this.is_admin),
      created_at: this.created_at
    };

    if (this.id) {
      await updateRecord('Users', this.id, { id: this.id, ...data });
    } else {
      const result = await addRecord('Users', data);
      this.id = result.id;
    }

    return this;
  }

  /**
   * Get user by Telegram ID
   */
  static async getByTelegramId(telegramId: number): Promise<User | null> {
    const [, record] = await findRecord('Users', 'telegram_id', telegramId);
    return record ? new User(record as IUser) : null;
  }

  /**
   * Get user by ID
   */
  static async getById(userId: number): Promise<User | null> {
    const [, record] = await findRecord('Users', 'id', userId);
    return record ? new User(record as IUser) : null;
  }

  /**
   * Get full name
   */
  get fullName(): string {
    if (this.first_name && this.last_name) {
      return `${this.first_name} ${this.last_name}`;
    }
    return this.first_name || this.username || String(this.telegram_id);
  }
}
