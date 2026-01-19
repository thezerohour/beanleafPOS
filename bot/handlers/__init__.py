"""
Handler initialization
"""

from .customer import setup_customer_handlers
from .admin import setup_admin_handlers
from .orders import setup_order_handlers

__all__ = ['setup_customer_handlers', 'setup_admin_handlers', 'setup_order_handlers']
