"""
Order and OrderItem models
"""

from datetime import datetime, UTC
import enum
from .database import add_record, update_record, find_record, get_all_records


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order:
    def __init__(self, id=None, user_id=None, total_amount=0.0, status='pending',
                 created_at=None, completed_at=None):
        self.id = int(id) if id else None
        self.user_id = int(user_id) if user_id else None
        self.total_amount = float(total_amount) if total_amount else 0.0
        self.status = str(status).lower() if status else 'pending'
        self.created_at = str(created_at) if created_at else datetime.now(UTC).isoformat()
        self.completed_at = str(completed_at) if completed_at else None
        self.items = []
    
    def save(self):
        """Save order to Google Sheets"""
        data = {
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'created_at': self.created_at,
            'completed_at': self.completed_at or ''
        }
        
        if self.id:
            data['id'] = self.id
            update_record('Orders', self.id, data)
        else:
            result = add_record('Orders', data)
            self.id = result['id']
        return self
    
    def get_items(self):
        """Get order items"""
        records = get_all_records('OrderItems')
        self.items = []
        for r in records:
            if str(r.get('order_id', '')) == str(self.id):
                self.items.append(OrderItem(
                    id=r.get('id'),
                    order_id=r.get('order_id'),
                    product_id=r.get('product_id'),
                    product_name=r.get('product_name'),
                    quantity=r.get('quantity', 0),
                    price=r.get('price', 0.0),
                    subtotal=r.get('subtotal', 0.0)
                ))
        return self.items
    
    @staticmethod
    def get_by_id(order_id):
        """Get order by ID"""
        _, record = find_record('Orders', 'id', order_id)
        if record:
            return Order(
                id=record.get('id'),
                user_id=record.get('user_id'),
                total_amount=record.get('total_amount', 0.0),
                status=record.get('status', 'pending'),
                created_at=record.get('created_at'),
                completed_at=record.get('completed_at')
            )
        return None
    
    @staticmethod
    def get_all_completed():
        """Get all completed orders"""
        records = get_all_records('Orders')
        orders = []
        for r in records:
            if r.get('status') == 'completed':
                orders.append(Order(
                    id=r.get('id'),
                    user_id=r.get('user_id'),
                    total_amount=r.get('total_amount', 0.0),
                    status=r.get('status', 'pending'),
                    created_at=r.get('created_at'),
                    completed_at=r.get('completed_at')
                ))
        return orders

    @staticmethod
    def get_all_pending():
        """Get all open orders (pending or paid)"""
        records = get_all_records('Orders')
        pending_orders = []
        for r in records:
            status = str(r.get('status', '')).lower()
            if status in (OrderStatus.PENDING.value, OrderStatus.PAID.value):
                pending_orders.append(Order(
                    id=r.get('id'),
                    user_id=r.get('user_id'),
                    total_amount=r.get('total_amount', 0.0),
                    status=r.get('status', 'pending'),
                    created_at=r.get('created_at'),
                    completed_at=r.get('completed_at')
                ))
        return pending_orders
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total_amount})>"


class OrderItem:
    def __init__(self, id=None, order_id=None, product_id=None, product_name=None,
                 quantity=0, price=0.0, subtotal=0.0):
        self.id = int(id) if id else None
        self.order_id = int(order_id) if order_id else None
        self.product_id = int(product_id) if product_id else None
        self.product_name = str(product_name) if product_name else ''
        self.quantity = int(float(quantity)) if quantity else 0
        self.price = float(price) if price else 0.0
        self.subtotal = float(subtotal) if subtotal else 0.0
    
    def save(self):
        """Save order item to Google Sheets"""
        data = {
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.subtotal
        }
        
        if self.id:
            data['id'] = self.id
            update_record('OrderItems', self.id, data)
        else:
            result = add_record('OrderItems', data)
            self.id = result['id']
        return self
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product='{self.product_name}', qty={self.quantity})>"
