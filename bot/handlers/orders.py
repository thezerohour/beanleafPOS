"""
Order processing handlers
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from ..models import Order, OrderItem, Product
from ..utils.helpers import get_or_create_user
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process checkout"""
    query = update.callback_query
    await query.answer()
    
    cart = context.user_data.get('cart', {}) if context.user_data else {}
    
    if not cart:
        await query.answer("❌ Your cart is empty!", show_alert=True)
        return
    
    user = update.effective_user
    try:
        db_user = get_or_create_user(None, user)
        
        # Calculate total and validate stock
        total_amount = 0
        order_items = []
        
        for product_id, quantity in cart.items():
            product = Product.get_by_id(product_id)
            
            if not product:
                await query.answer(f"❌ Product not found!", show_alert=True)
                return
            
            if product.stock < quantity:
                await query.answer(
                    f"❌ Not enough stock for {product.name}. Available: {product.stock}",
                    show_alert=True
                )
                return
            
            subtotal = product.price * quantity
            total_amount += subtotal
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        
        # Create order as pending so store can confirm
        order = Order(
            user_id=db_user.id,
            total_amount=total_amount,
            status='pending',
            created_at=datetime.now(UTC).isoformat(),
            completed_at=None
        )
        order.save()
        
        # Create order items (stock will be decremented when store accepts)
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                product_name=item['product'].name,
                quantity=item['quantity'],
                price=item['product'].price,
                subtotal=item['subtotal']
            )
            order_item.save()
        
        # Clear cart
        context.user_data['cart'] = {}
        
        # Build pending confirmation message
        lines = [
            "✅ Order placed!",
            "Status: Pending store confirmation",
            f"Order ID: #{order.id}",
            f"Total: ${total_amount:.2f}",
            "\nItems:"
        ]
        for item in order_items:
            lines.append(
                f"• {item['product'].name} — {item['quantity']} x ${item['product'].price:.2f} = ${item['subtotal']:.2f}"
            )
        message = "\n".join(lines)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ Shop Again", callback_data="browse")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        await query.answer("❌ An error occurred during checkout.", show_alert=True)


def setup_order_handlers(application):
    """Set up order processing handlers"""
    application.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
