"""
Database setup and configuration using Google Sheets
"""

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Google Sheets configuration
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

# Global client and caches
_client = None
_spreadsheet = None
_worksheet_cache = {}


def get_google_client():
    """Get authenticated Google Sheets client"""
    global _client, _spreadsheet
    
    if _client is None:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_CREDENTIALS_FILE, scopes=scope
            )
            _client = gspread.authorize(creds)
            _spreadsheet = _client.open_by_key(GOOGLE_SHEET_ID)
        except FileNotFoundError:
            raise Exception(f"Credentials file not found: {GOOGLE_CREDENTIALS_FILE}")
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Sheets: {e}")
    
    return _client, _spreadsheet


def init_db():
    """Initialize Google Sheets with necessary worksheets and headers"""
    client, spreadsheet = get_google_client()
    
    # Define worksheets and their headers
    worksheets = {
        'Users': ['id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_admin', 'created_at'],
        'Products': ['id', 'name', 'description', 'price', 'stock', 'is_available', 'created_at', 'updated_at'],
        'Orders': ['id', 'user_id', 'total_amount', 'status', 'created_at', 'completed_at'],
        'OrderItems': ['id', 'order_id', 'product_id', 'product_name', 'quantity', 'price', 'subtotal']
    }
    
    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
    
    for sheet_name, headers in worksheets.items():
        if sheet_name not in existing_sheets:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
            worksheet.append_row(headers)
            print(f"Created worksheet: {sheet_name}")
        else:
            worksheet = spreadsheet.worksheet(sheet_name)
            # Check if headers exist, if not add them
            header_row = worksheet.row_values(1)
            if not header_row:
                worksheet.append_row(headers)
                print(f"Added headers to worksheet: {sheet_name}")
        # cache worksheet
        _worksheet_cache[sheet_name] = worksheet


def get_worksheet(sheet_name):
    """Get a specific worksheet"""
    global _worksheet_cache
    if sheet_name in _worksheet_cache:
        return _worksheet_cache[sheet_name]
    client, spreadsheet = get_google_client()
    ws = spreadsheet.worksheet(sheet_name)
    _worksheet_cache[sheet_name] = ws
    return ws


def get_next_id(sheet_name):
    """Get the next available ID for a sheet"""
    worksheet = get_worksheet(sheet_name)
    try:
        records = worksheet.get_all_records()
        if not records:
            return 1
        return max([int(record.get('id', 0)) for record in records]) + 1
    except IndexError:
        # Empty worksheet with only headers (or no data)
        return 1
    except Exception as e:
        print(f"Error getting next ID for {sheet_name}: {e}")
        return 1


def find_record(sheet_name, field, value):
    """Find a record by field value"""
    worksheet = get_worksheet(sheet_name)
    records = worksheet.get_all_records()
    for idx, record in enumerate(records, start=2):  # Start at 2 because row 1 is headers
        if str(record.get(field)) == str(value):
            return idx, record
    return None, None


def add_record(sheet_name, data):
    """Add a new record to a sheet"""
    worksheet = get_worksheet(sheet_name)
    data['id'] = get_next_id(sheet_name)
    
    # Get headers to ensure correct order
    try:
        headers = worksheet.row_values(1)
    except Exception:
        headers = []
    
    if not headers:
        # Initialize headers from data keys
        headers = list(data.keys())
        try:
            worksheet.insert_row(headers, index=1)
        except Exception:
            worksheet.append_row(headers)
    
    row = [str(data.get(header, '')) for header in headers]
    worksheet.append_row(row)
    return data


def update_record(sheet_name, record_id, data):
    """Update an existing record"""
    worksheet = get_worksheet(sheet_name)
    row_num, _ = find_record(sheet_name, 'id', record_id)
    
    if row_num:
        try:
            headers = worksheet.row_values(1)
        except Exception:
            headers = []
        
        if not headers:
            raise ValueError(f"No headers found in {sheet_name} worksheet")
        
        row = [str(data.get(header, '')) for header in headers]
        for col_num, value in enumerate(row, start=1):
            worksheet.update_cell(row_num, col_num, value)
        return True
    return False


def delete_record(sheet_name, record_id):
    """Delete a record from a sheet"""
    worksheet = get_worksheet(sheet_name)
    row_num, _ = find_record(sheet_name, 'id', record_id)
    
    if row_num:
        worksheet.delete_rows(row_num)
        return True
    return False


def get_all_records(sheet_name):
    """Get all records from a sheet"""
    worksheet = get_worksheet(sheet_name)
    try:
        return worksheet.get_all_records()
    except IndexError:
        # Empty worksheet with no data rows (only headers or completely empty)
        return []
    except Exception as e:
        print(f"Error getting records from {sheet_name}: {e}")
        return []


class SheetSession:
    """Mock session class for compatibility"""
    
    def __init__(self):
        pass
    
    def query(self, model):
        return SheetQuery(model)
    
    def add(self, obj):
        obj._pending_add = True
    
    def commit(self):
        pass
    
    def rollback(self):
        pass
    
    def refresh(self, obj):
        pass
    
    def flush(self):
        pass
    
    def close(self):
        pass


class SheetQuery:
    """Mock query class for compatibility"""
    
    def __init__(self, model):
        self.model = model
        self._filters = []
    
    def filter(self, *args):
        self._filters.extend(args)
        return self
    
    def first(self):
        # Implementation depends on the model
        return None
    
    def all(self):
        # Implementation depends on the model
        return []
    
    def count(self):
        return len(self.all())


def get_session():
    """Get a session (for compatibility)"""
    return SheetSession()
