"""
Helper functions
"""

import os
from datetime import datetime
from ..models import User
from dotenv import load_dotenv

load_dotenv()

ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))


def get_or_create_user(db, telegram_user):
    """Get or create user in database"""
    user = User.get_by_telegram_id(telegram_user.id)
    
    if not user:
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            is_admin=(telegram_user.id == ADMIN_USER_ID)
        )
        user.save()
    
    return user


def is_admin(telegram_user_id):
    """Check if user is admin"""
    return telegram_user_id == ADMIN_USER_ID


def generate_receipt(order, order_items):
    """Generate order receipt"""
    def _format_dt(value):
        try:
            from datetime import datetime
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except Exception:
                    return value
            else:
                dt = value
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return str(value)

    display_date = _format_dt(order.completed_at or order.created_at)

    receipt = "🧾 *Order Receipt*\n"
    receipt += "=" * 30 + "\n\n"
    receipt += f"📋 Order ID: #{order.id}\n"
    receipt += f"📅 Date: {display_date}\n\n"
    receipt += "*Items:*\n"
    
    for item in order_items:
        receipt += f"• {item['product'].name}\n"
        receipt += f"  {item['quantity']} x ${item['product'].price:.2f} = ${item['subtotal']:.2f}\n"
    
    receipt += "\n" + "=" * 30 + "\n"
    receipt += f"💰 *Total: ${order.total_amount:.2f}*\n\n"
    receipt += "Thank you for your purchase! 🎉"
    
    return receipt


def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"


def validate_price(price_str):
    """Validate and parse price string"""
    try:
        price = float(price_str)
        if price < 0:
            return None, "Price cannot be negative"
        return price, None
    except ValueError:
        return None, "Invalid price format"


def validate_stock(stock_str):
    """Validate and parse stock string"""
    try:
        stock = int(stock_str)
        if stock < 0:
            return None, "Stock cannot be negative"
        return stock, None
    except ValueError:
        return None, "Invalid stock format"
