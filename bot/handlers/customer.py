"""
Customer command handlers
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest
from ..models import Product
from ..utils.keyboards import get_main_menu_keyboard, get_products_keyboard
from ..utils.helpers import get_or_create_user
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    try:
        logger.info(f"Start command from user: {user.id} (@{user.username})")
        db_user = get_or_create_user(None, user)
        logger.info(f"User created/retrieved: {db_user}")
        
        welcome_message = f"👋 Welcome to BeanLeaf POS, {db_user.full_name}!\n\n"
        welcome_message += "🛍️ Browse our products and place orders easily.\n\n"
        welcome_message += "Use the menu below to get started:"
        
        keyboard = get_main_menu_keyboard(db_user.is_admin)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=keyboard
        )
        logger.info(f"Welcome message sent to user {user.id}")
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        try:
            await update.message.reply_text("❌ An error occurred. Please try again.")
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")


async def browse_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available products"""
    query = update.callback_query
    if query:
        await query.answer()
    
    try:
        products = Product.get_all(available_only=True)
        
        if not products:
            message = "❌ No products available at the moment."
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        else:
            message = "🛍️ *Available Products*\n\n"
            keyboard = get_products_keyboard(products)
        
        if query:
            await query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error browsing products: {e}")
        error_msg = "❌ Error loading products. Please try again."
        if query:
            await query.answer(error_msg, show_alert=True)
        else:
            await update.message.reply_text(error_msg)


async def view_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View product details"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split('_')[1])
    
    try:
        product = Product.get_by_id(product_id)
        
        if not product:
            await query.edit_message_text("❌ Product not found.")
            return
        
        message = f"🏷️ *{product.name}*\n\n"
        message += f"💰 Price: ${product.price:.2f}\n"
        if product.description:
            message += f"📝 {product.description}\n"
        message += f"\n📦 Stock: {product.stock} available\n"
        
        # Show how many are already in the user's cart to avoid identical message edits
        cart_qty = (context.user_data.get('cart', {}) if context.user_data else {}).get(product.id, 0)
        if cart_qty:
            message += f"🛒 In your cart: {cart_qty}\n"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add to Cart", callback_data=f"addcart_{product_id}")],
            [InlineKeyboardButton("◀️ Back to Products", callback_data="browse")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
        
        try:
            await query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except BadRequest as e:
            # Telegram raises on identical content; ignore that specific case
            if 'message is not modified' in str(e).lower():
                return
            raise
    except Exception as e:
        logger.error(f"Error viewing product: {e}")
        await query.answer("❌ Error loading product.", show_alert=True)


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View shopping cart"""
    query = update.callback_query
    if query:
        await query.answer()
    
    cart = context.user_data.get('cart', {}) if context.user_data else {}
    
    if not cart:
        message = "🛒 Your cart is empty.\n\nBrowse products to add items!"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ Browse Products", callback_data="browse")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    else:
        try:
            message = "🛒 *Your Shopping Cart*\n\n"
            total = 0
            
            for product_id, quantity in cart.items():
                product = Product.get_by_id(product_id)
                if product:
                    subtotal = product.price * quantity
                    total += subtotal
                    message += f"• {product.name} x{quantity} = ${subtotal:.2f}\n"
            
            message += f"\n💰 *Total: ${total:.2f}*"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Checkout", callback_data="checkout")],
                [InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")],
                [InlineKeyboardButton("🛍️ Continue Shopping", callback_data="browse")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        except Exception as e:
            logger.error(f"Error viewing cart: {e}")
            message = "❌ Error loading cart."
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
    
    if query:
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add product to cart"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split('_')[1])
    
    cart = context.user_data.get('cart', {}) if context.user_data else {}
    cart[product_id] = cart.get(product_id, 0) + 1
    context.user_data['cart'] = cart
    
    await query.answer("✅ Added to cart!", show_alert=True)
    await view_product(update, context)


async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear shopping cart"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['cart'] = {}
    
    await query.answer("🗑️ Cart cleared!", show_alert=True)
    await view_cart(update, context)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    try:
        db_user = get_or_create_user(None, user)
        
        message = "🏠 *Main Menu*\n\nWhat would you like to do?"
        keyboard = get_main_menu_keyboard(db_user.is_admin)
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in main menu: {e}")
        await query.answer("❌ Error loading menu.", show_alert=True)

def setup_customer_handlers(application):
    """Set up customer command handlers"""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(browse_products, pattern="^browse$"))
    application.add_handler(CallbackQueryHandler(view_product, pattern="^product_"))
    application.add_handler(CallbackQueryHandler(view_cart, pattern="^cart$"))
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern="^addcart_"))
    application.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
