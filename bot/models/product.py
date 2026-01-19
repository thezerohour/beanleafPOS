"""
Product model
"""

from datetime import datetime, UTC
from .database import get_worksheet, add_record, update_record, find_record, get_all_records


class Product:
    def __init__(self, id=None, name=None, description=None, price=0.0, stock=0, 
                 is_available=True, created_at=None, updated_at=None):
        self.id = int(id) if id else None
        self.name = str(name) if name else ''
        self.description = str(description) if description else ''
        self.price = float(price) if price else 0.0
        self.stock = int(float(stock)) if stock else 0
        self.is_available = str(is_available).lower() == 'true' if isinstance(is_available, str) else bool(is_available)
        self.created_at = str(created_at) if created_at else datetime.now(UTC).isoformat()
        self.updated_at = str(updated_at) if updated_at else datetime.now(UTC).isoformat()
    
    def save(self):
        """Save product to Google Sheets"""
        data = {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'is_available': str(self.is_available),
            'created_at': self.created_at,
            'updated_at': datetime.now(UTC).isoformat()
        }
        
        if self.id:
            data['id'] = self.id
            update_record('Products', self.id, data)
        else:
            result = add_record('Products', data)
            self.id = result['id']
        return self
    
    @staticmethod
    def get_by_id(product_id):
        """Get product by ID"""
        _, record = find_record('Products', 'id', product_id)
        if record:
            return Product(**record)
        return None
    
    @staticmethod
    def get_all(available_only=False):
        """Get all products"""
        records = get_all_records('Products')
        products = [Product(**record) for record in records]
        if available_only:
            products = [p for p in products if p.is_available]
        return products
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'is_available': self.is_available
        }
