/**
 * Product model
 */

import { addRecord, updateRecord, findRecord, getAllRecords } from './database';

export interface IProduct {
  id?: number;
  name: string;
  description: string;
  price: number;
  stock: number;
  is_available: boolean | string;
  created_at?: string;
  updated_at?: string;
}

export class Product {
  id?: number;
  name: string;
  description: string;
  price: number;
  stock: number;
  is_available: boolean;
  created_at: string;
  updated_at: string;

  constructor(data: IProduct) {
    this.id = data.id ? parseInt(String(data.id)) : undefined;
    this.name = String(data.name || '');
    this.description = String(data.description || '');
    this.price = parseFloat(String(data.price || 0));
    this.stock = parseInt(String(data.stock || 0));
    
    // Handle boolean conversion for is_available
    if (typeof data.is_available === 'string') {
      this.is_available = data.is_available.toLowerCase() === 'true';
    } else {
      this.is_available = Boolean(data.is_available !== false);
    }
    
    this.created_at = data.created_at || new Date().toISOString();
    this.updated_at = data.updated_at || new Date().toISOString();
  }

  /**
   * Save product to Google Sheets
   */
  async save(): Promise<Product> {
    const data = {
      name: this.name,
      description: this.description,
      price: this.price,
      stock: this.stock,
      is_available: String(this.is_available),
      created_at: this.created_at,
      updated_at: new Date().toISOString()
    };

    if (this.id) {
      await updateRecord('Products', this.id, { id: this.id, ...data });
    } else {
      const result = await addRecord('Products', data);
      this.id = result.id;
    }

    return this;
  }

  /**
   * Get product by ID
   */
  static async getById(productId: number): Promise<Product | null> {
    const [, record] = await findRecord('Products', 'id', productId);
    return record ? new Product(record as IProduct) : null;
  }

  /**
   * Get all products
   */
  static async getAll(availableOnly: boolean = false): Promise<Product[]> {
    const records = await getAllRecords('Products');
    let products = records.map(record => new Product(record as IProduct));

    if (availableOnly) {
      products = products.filter(p => p.is_available);
    }

    return products;
  }

  /**
   * Convert to plain object
   */
  toDict(): IProduct {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      price: this.price,
      stock: this.stock,
      is_available: this.is_available
    };
  }
}
