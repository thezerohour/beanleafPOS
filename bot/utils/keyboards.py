"""
Keyboard layouts for bot interactions
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard(is_admin=False):
    """Get main menu keyboard"""
    # Ensure is_admin is a boolean
    if isinstance(is_admin, str):
        is_admin = is_admin.lower() == 'true'
    else:
        is_admin = bool(is_admin)
    
    buttons = [
        [InlineKeyboardButton("🛍️ Browse Products", callback_data="browse")],
        [InlineKeyboardButton("🛒 View Cart", callback_data="cart")],
    ]
    
    if is_admin:
        buttons.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin")])
    
    return InlineKeyboardMarkup(buttons)


def get_products_keyboard(products):
    """Get products listing keyboard"""
    buttons = []
    
    for product in products:
        button_text = f"{product.name} - ${product.price:.2f}"
        if product.stock == 0:
            button_text += " (Out of Stock)"
        
        buttons.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"product_{product.id}"
            )
        ])
    
    buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(buttons)


def get_admin_keyboard():
    """Get admin panel keyboard"""
    buttons = [
        [InlineKeyboardButton("➕ Add Product", callback_data="admin_add_product")],
        [InlineKeyboardButton("📥 Order Queue", callback_data="admin_order_queue")],
        [InlineKeyboardButton("📦 Manage Products", callback_data="admin_products")],
        [InlineKeyboardButton("📊 Sales Statistics", callback_data="admin_sales")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(buttons)
