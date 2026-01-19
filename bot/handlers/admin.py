"""
Admin command handlers
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from ..models import Product, Order, User, OrderStatus
from ..utils.helpers import get_or_create_user, is_admin
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)

# Conversation states
ADD_PRODUCT_NAME, ADD_PRODUCT_DESC, ADD_PRODUCT_PRICE, ADD_PRODUCT_STOCK = range(4)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    query = update.callback_query
    if query:
        await query.answer()
    
    user = update.effective_user
    try:
        db_user = get_or_create_user(None, user)
        
        if not db_user.is_admin:
            message = "❌ You don't have admin access."
            if query:
                await query.answer(message, show_alert=True)
            else:
                await update.message.reply_text(message)
            return
        
        message = "🔧 *Admin Panel*\n\nManage your POS system:"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Product", callback_data="admin_add_product")],
            [InlineKeyboardButton("📥 Order Queue", callback_data="admin_order_queue")],
            [InlineKeyboardButton("📦 Manage Products", callback_data="admin_products")],
            [InlineKeyboardButton("📊 Sales Statistics", callback_data="admin_sales")],
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
    except Exception as e:
        logger.error(f"Error in admin panel: {e}")
        if query:
            await query.answer("❌ Error loading admin panel.", show_alert=True)


async def manage_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product management"""
    query = update.callback_query
    await query.answer()
    
    try:
        products = Product.get_all()
        
        if not products:
            message = "📦 No products found.\n\nAdd your first product!"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Product", callback_data="admin_add_product")],
                [InlineKeyboardButton("◀️ Back", callback_data="admin")]
            ])
        else:
            message = "📦 *Product Management*\n\n"
            
            buttons = []
            for product in products:
                status = "✅" if product.is_available else "❌"
                buttons.append([
                    InlineKeyboardButton(
                        f"{status} {product.name} - ${product.price:.2f} (Stock: {product.stock})",
                        callback_data=f"admin_edit_{product.id}"
                    )
                ])
            
            buttons.append([InlineKeyboardButton("➕ Add Product", callback_data="admin_add_product")])
            buttons.append([InlineKeyboardButton("◀️ Back", callback_data="admin")])
            keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error managing products: {e}")
        await query.answer("❌ Error loading products.", show_alert=True)


async def sales_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sales statistics"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Get all completed orders
        orders = Order.get_all_completed()
        
        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        
        message = "📊 *Sales Statistics*\n\n"
        message += f"📦 Total Orders: {total_orders}\n"
        message += f"💰 Total Revenue: ${total_revenue:.2f}\n"
        message += f"📈 Average Order: ${avg_order:.2f}\n"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="admin")]
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error loading sales statistics: {e}")
        await query.answer("❌ Error loading statistics.", show_alert=True)


async def order_queue(update: Update, context: ContextTypes.DEFAULT_TYPE, notice: str | None = None):
    """Display pending order queue for store side"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    db_user = get_or_create_user(None, user)

    if not db_user.is_admin:
        await query.answer("❌ Admins only", show_alert=True)
        return

    open_orders = Order.get_all_pending()

    if not open_orders:
        message = "📥 *Order Queue*\n\nNo pending orders right now."
        if notice:
            message += f"\n\n{notice}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="admin")]
        ])
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
        return

    lines = ["📥 *Order Queue*\n"]
    if notice:
        lines.append(f"{notice}\n")

    buttons = []
    for order in open_orders:
        items = order.get_items()
        item_summary = ", ".join([f"{item.quantity} x {item.product_name}" for item in items]) or "No items"
        status_label = "Pending" if str(order.status).lower() == OrderStatus.PENDING.value else "Paid"
        lines.append(f"• Order #{order.id} — ${order.total_amount:.2f} ({status_label})\n  Items: {item_summary}\n")
        if str(order.status).lower() == OrderStatus.PENDING.value:
            buttons.append([
                InlineKeyboardButton(f"💵 Mark Paid #{order.id}", callback_data=f"order_paid_{order.id}"),
                InlineKeyboardButton(f"❌ Decline #{order.id}", callback_data=f"order_decline_{order.id}")
            ])
        else:
            buttons.append([
                InlineKeyboardButton(f"✅ Mark Completed #{order.id}", callback_data=f"order_complete_{order.id}"),
                InlineKeyboardButton(f"❌ Decline #{order.id}", callback_data=f"order_decline_{order.id}")
            ])

    buttons.append([InlineKeyboardButton("◀️ Back", callback_data="admin")])
    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("\n".join(lines), reply_markup=keyboard, parse_mode='Markdown')


async def _process_order(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    """Process order actions: paid, complete, decline"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    db_user = get_or_create_user(None, user)

    if not db_user.is_admin:
        await query.answer("❌ Admins only", show_alert=True)
        return

    try:
        order_id = int(query.data.split("_")[-1])
    except ValueError:
        await query.answer("❌ Invalid order ID", show_alert=True)
        return

    order = Order.get_by_id(order_id)
    if not order:
        await query.answer("❌ Order not found", show_alert=True)
        return

    items = order.get_items()
    if action == 'paid':
        if str(order.status).lower() != OrderStatus.PENDING.value:
            await query.answer("⚠️ Order not pending", show_alert=True)
            return
        for item in items:
            product = Product.get_by_id(item.product_id)
            if not product or product.stock < item.quantity:
                await query.answer(f"❌ Not enough stock for {item.product_name}", show_alert=True)
                return
        for item in items:
            product = Product.get_by_id(item.product_id)
            product.stock -= item.quantity
            product.save()
        order.status = OrderStatus.PAID.value
        notice = f"💵 Order #{order.id} marked paid"
        try:
            user_row = User.get_by_id(order.user_id)
            chat_id = user_row.telegram_id if user_row else None
            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"💵 Your order #{order.id} is paid and being prepared."
                )
        except Exception:
            logger.warning("Could not notify customer for order %s", order.id)

    elif action == 'complete':
        if str(order.status).lower() not in (OrderStatus.PAID.value, OrderStatus.PENDING.value):
            await query.answer("⚠️ Order cannot be completed", show_alert=True)
            return
        order.status = OrderStatus.COMPLETED.value
        order.completed_at = datetime.now(UTC).isoformat()
        notice = f"✅ Order #{order.id} completed"
        try:
            user_row = User.get_by_id(order.user_id)
            chat_id = user_row.telegram_id if user_row else None
            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ Your order #{order.id} is ready for collection!"
                )
        except Exception:
            logger.warning("Could not notify customer for order %s", order.id)

    else:
        if str(order.status).lower() not in (OrderStatus.PENDING.value, OrderStatus.PAID.value):
            await query.answer("⚠️ Order already processed", show_alert=True)
            return
        order.status = 'cancelled'
        order.completed_at = datetime.now(UTC).isoformat()
        notice = f"❌ Order #{order.id} declined"
        try:
            user_row = User.get_by_id(order.user_id)
            chat_id = user_row.telegram_id if user_row else None
            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ Your order #{order.id} was declined. Please contact the store."
                )
            else:
                logger.warning("No telegram_id for order %s user %s", order.id, order.user_id)
        except Exception:
            logger.warning("Could not notify customer for order %s", order.id)

    order.save()
    await order_queue(update, context, notice=notice)


async def accept_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _process_order(update, context, action='paid')


async def decline_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _process_order(update, context, action='decline')


async def complete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _process_order(update, context, action='complete')


async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new product"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "➕ *Add New Product*\n\nPlease enter the product name:",
        parse_mode='Markdown'
    )
    
    return ADD_PRODUCT_NAME


async def cancel_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel adding product"""
    await update.message.reply_text("❌ Product addition cancelled.")
    return ConversationHandler.END


def setup_admin_handlers(application):
    """Set up admin command handlers"""
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin$"))
    application.add_handler(CallbackQueryHandler(manage_products, pattern="^admin_products$"))
    application.add_handler(CallbackQueryHandler(sales_statistics, pattern="^admin_sales$"))
    application.add_handler(CallbackQueryHandler(order_queue, pattern="^admin_order_queue$"))
    application.add_handler(CallbackQueryHandler(accept_order, pattern="^order_accept_\\d+$"))
    application.add_handler(CallbackQueryHandler(accept_order, pattern="^order_paid_\\d+$"))
    application.add_handler(CallbackQueryHandler(complete_order, pattern="^order_complete_\\d+$"))
    application.add_handler(CallbackQueryHandler(decline_order, pattern="^order_decline_\\d+$"))
