/**
 * Order and OrderItem models
 */

import { addRecord, updateRecord, findRecord, getAllRecords } from './database';

export enum OrderStatus {
  PENDING = 'pending',
  PAID = 'paid',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export interface IOrder {
  id?: number;
  user_id: number;
  total_amount?: number;
  status?: string;
  created_at?: string;
  completed_at?: string | null;
}

export interface IOrderItem {
  id?: number;
  order_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  price: number;
  subtotal: number;
}

export class OrderItem {
  id?: number;
  order_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  price: number;
  subtotal: number;

  constructor(data: IOrderItem) {
    this.id = data.id ? parseInt(String(data.id)) : undefined;
    this.order_id = parseInt(String(data.order_id));
    this.product_id = parseInt(String(data.product_id));
    this.product_name = String(data.product_name);
    this.quantity = parseInt(String(data.quantity || 0));
    this.price = parseFloat(String(data.price || 0));
    this.subtotal = parseFloat(String(data.subtotal || 0));
  }

  /**
   * Save order item to Google Sheets
   */
  async save(): Promise<OrderItem> {
    const data = {
      order_id: this.order_id,
      product_id: this.product_id,
      product_name: this.product_name,
      quantity: this.quantity,
      price: this.price,
      subtotal: this.subtotal
    };

    if (this.id) {
      await updateRecord('OrderItems', this.id, { id: this.id, ...data });
    } else {
      const result = await addRecord('OrderItems', data);
      this.id = result.id;
    }

    return this;
  }
}

export class Order {
  id?: number;
  user_id: number;
  total_amount: number;
  status: string;
  created_at: string;
  completed_at: string | null;
  items: OrderItem[];

  constructor(data: IOrder) {
    this.id = data.id ? parseInt(String(data.id)) : undefined;
    this.user_id = parseInt(String(data.user_id));
    this.total_amount = parseFloat(String(data.total_amount || 0));
    this.status = String(data.status || OrderStatus.PENDING).toLowerCase();
    this.created_at = data.created_at || new Date().toISOString();
    this.completed_at = data.completed_at || null;
    this.items = [];
  }

  /**
   * Save order to Google Sheets
   */
  async save(): Promise<Order> {
    const data = {
      user_id: this.user_id,
      total_amount: this.total_amount,
      status: this.status,
      created_at: this.created_at,
      completed_at: this.completed_at || ''
    };

    if (this.id) {
      await updateRecord('Orders', this.id, { id: this.id, ...data });
    } else {
      const result = await addRecord('Orders', data);
      this.id = result.id;
    }

    return this;
  }

  /**
   * Get order items
   */
  async getItems(): Promise<OrderItem[]> {
    const records = await getAllRecords('OrderItems');
    this.items = [];

    for (const record of records) {
      if (String(record.order_id) === String(this.id)) {
        this.items.push(new OrderItem(record as IOrderItem));
      }
    }

    return this.items;
  }

  /**
   * Get order by ID
   */
  static async getById(orderId: number): Promise<Order | null> {
    const [, record] = await findRecord('Orders', 'id', orderId);
    return record ? new Order(record as IOrder) : null;
  }

  /**
   * Get all completed orders
   */
  static async getAllCompleted(): Promise<Order[]> {
    const records = await getAllRecords('Orders');
    return records
      .filter(r => r.status === OrderStatus.COMPLETED)
      .map(r => new Order(r as IOrder));
  }

  /**
   * Get all pending orders
   */
  static async getAllPending(): Promise<Order[]> {
    const records = await getAllRecords('Orders');
    return records
      .filter(r => r.status === OrderStatus.PENDING || r.status === OrderStatus.PAID)
      .map(r => new Order(r as IOrder));
  }
}
