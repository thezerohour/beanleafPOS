/**
 * Database setup and configuration using Google Sheets
 */

import { GoogleSpreadsheet, GoogleSpreadsheetRow } from 'google-spreadsheet';
import { JWT } from 'google-auth-library';
import * as dotenv from 'dotenv';

dotenv.config();

// Google Sheets configuration
const GOOGLE_SHEET_ID = process.env.GOOGLE_SHEET_ID || '';
const GOOGLE_CREDENTIALS_FILE = process.env.GOOGLE_CREDENTIALS_FILE || 'credentials.json';

// Global client and caches
let doc: GoogleSpreadsheet | null = null;
const worksheetCache: Map<string, any> = new Map();

interface WorksheetHeaders {
  [key: string]: string[];
}

/**
 * Get authenticated Google Sheets document
 */
export async function getGoogleClient(): Promise<GoogleSpreadsheet> {
  if (!doc) {
    try {
      // Load credentials
      const credentials = require(`../../${GOOGLE_CREDENTIALS_FILE}`);
      
      const serviceAccountAuth = new JWT({
        email: credentials.client_email,
        key: credentials.private_key,
        scopes: [
          'https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.file',
        ],
      });

      doc = new GoogleSpreadsheet(GOOGLE_SHEET_ID, serviceAccountAuth);
      await doc.loadInfo();
    } catch (error) {
      throw new Error(`Failed to authenticate with Google Sheets: ${error}`);
    }
  }

  return doc;
}

/**
 * Initialize Google Sheets with necessary worksheets and headers
 */
export async function initDb(): Promise<void> {
  const spreadsheet = await getGoogleClient();

  // Define worksheets and their headers
  const worksheets: WorksheetHeaders = {
    'Users': ['id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_admin', 'created_at'],
    'Products': ['id', 'name', 'description', 'price', 'stock', 'is_available', 'created_at', 'updated_at'],
    'Orders': ['id', 'user_id', 'total_amount', 'status', 'created_at', 'completed_at'],
    'OrderItems': ['id', 'order_id', 'product_id', 'product_name', 'quantity', 'price', 'subtotal']
  };

  for (const [sheetName, headers] of Object.entries(worksheets)) {
    let sheet = spreadsheet.sheetsByTitle[sheetName];
    
    if (!sheet) {
      sheet = await spreadsheet.addSheet({
        title: sheetName,
        headerValues: headers
      });
      console.log(`Created worksheet: ${sheetName}`);
    } else {
      await sheet.loadHeaderRow();
      if (sheet.headerValues.length === 0) {
        await sheet.setHeaderRow(headers);
        console.log(`Added headers to worksheet: ${sheetName}`);
      }
    }
    
    worksheetCache.set(sheetName, sheet);
  }
}

/**
 * Get a specific worksheet
 */
export async function getWorksheet(sheetName: string): Promise<any> {
  if (worksheetCache.has(sheetName)) {
    return worksheetCache.get(sheetName);
  }

  const spreadsheet = await getGoogleClient();
  const sheet = spreadsheet.sheetsByTitle[sheetName];
  
  if (!sheet) {
    throw new Error(`Worksheet not found: ${sheetName}`);
  }

  await sheet.loadHeaderRow();
  worksheetCache.set(sheetName, sheet);
  return sheet;
}

/**
 * Get the next available ID for a sheet
 */
export async function getNextId(sheetName: string): Promise<number> {
  const worksheet = await getWorksheet(sheetName);
  const rows = await worksheet.getRows();

  if (rows.length === 0) {
    return 1;
  }

  const ids = rows.map((row: GoogleSpreadsheetRow) => parseInt(row.get('id') || '0'));
  return Math.max(...ids, 0) + 1;
}

/**
 * Add a record to a worksheet
 */
export async function addRecord(sheetName: string, data: Record<string, any>): Promise<Record<string, any>> {
  const worksheet = await getWorksheet(sheetName);
  const nextId = await getNextId(sheetName);
  
  const recordData = { id: nextId, ...data };
  await worksheet.addRow(recordData);
  
  return recordData;
}

/**
 * Update a record in a worksheet
 */
export async function updateRecord(sheetName: string, id: number, data: Record<string, any>): Promise<void> {
  const worksheet = await getWorksheet(sheetName);
  const rows = await worksheet.getRows();
  
  const row = rows.find((r: GoogleSpreadsheetRow) => parseInt(r.get('id')) === id);
  
  if (row) {
    Object.entries(data).forEach(([key, value]) => {
      row.set(key, value);
    });
    await row.save();
  }
}

/**
 * Find a record in a worksheet
 */
export async function findRecord(sheetName: string, field: string, value: any): Promise<[number, Record<string, any> | null]> {
  const worksheet = await getWorksheet(sheetName);
  const rows = await worksheet.getRows();
  
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    if (String(row.get(field)) === String(value)) {
      const record: Record<string, any> = {};
      worksheet.headerValues.forEach((header: string) => {
        record[header] = row.get(header);
      });
      return [i + 2, record]; // +2 because row 1 is headers
    }
  }
  
  return [-1, null];
}

/**
 * Get all records from a worksheet
 */
export async function getAllRecords(sheetName: string): Promise<Record<string, any>[]> {
  const worksheet = await getWorksheet(sheetName);
  const rows = await worksheet.getRows();
  
  return rows.map((row: GoogleSpreadsheetRow) => {
    const record: Record<string, any> = {};
    worksheet.headerValues.forEach((header: string) => {
      record[header] = row.get(header);
    });
    return record;
  });
}
