# BeanLeaf POS - Telegram Bot Point of Sale

A feature-rich Telegram bot that serves as a complete point-of-sale (POS) system for small businesses, **powered by Google Sheets** for easy data management.

## Features

- 🛍️ **Product Management**: Add, edit, delete products with prices and descriptions
- 🛒 **Shopping Cart**: Build orders with multiple items
- 💳 **Order Processing**: Complete checkout and generate receipts
- 📊 **Sales Tracking**: View sales history and statistics
- 👥 **User Roles**: Admin and customer access levels
- 📦 **Inventory Management**: Track stock levels
- 📱 **Intuitive Interface**: Easy-to-use inline keyboard menus
- 📈 **Google Sheets Backend**: View and manage all data in real-time via spreadsheet

## Why Google Sheets?

✅ **No Database Server Needed** - Easy setup, no technical database knowledge required  
✅ **Real-time Data Access** - View and edit products, orders, and users directly in the spreadsheet  
✅ **Automatic Backups** - Built-in version history and cloud storage  
✅ **Collaborative** - Multiple people can access and manage data  
✅ **Data Analysis** - Use spreadsheet formulas, charts, and filters  

## Requirements

- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Google account with access to Google Sheets

## Quick Start

### 1. Clone the repository
```bash
cd beanleafPOS
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up Google Sheets (IMPORTANT!)

Follow the detailed guide in [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) to:
- Create a Google Sheet
- Set up Google Cloud credentials
- Share the sheet with your service account

**Quick summary:**
1. Create a Google Sheet and note its ID
2. Enable Google Sheets API in Google Cloud Console
3. Create a service account and download `credentials.json`
4. Share the sheet with the service account email
5. Place `credentials.json` in the project root

### 5. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
BOT_TOKEN=your_telegram_bot_token
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_CREDENTIALS_FILE=credentials.json
ADMIN_USER_ID=your_telegram_user_id
```

### 6. Run the bot
```bash
python bot/main.py
```

The bot will automatically create necessary worksheets in your Google Sheet on first run!

## Usage

### Customer Commands
- `/start` - Start the bot and view main menu
- `/browse` - Browse available products
- `/cart` - View your shopping cart
- `/checkout` - Complete your order

### Admin Commands
- `/admin` - Access admin panel
- `/addproduct` - Add a new product
- `/editproduct` - Edit existing product
- `/deleteproduct` - Remove a product
- `/sales` - View sales statistics
- `/inventory` - Manage inventory

## Project Structure

```
beanleafPOS/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Main bot application
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── admin.py         # Admin command handlers
│   │   ├── customer.py      # Customer command handlers
│   │   └── orders.py        # Order processing handlers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py      # Database setup
│   │   ├── product.py       # Product model
│   │   ├── order.py         # Order model
│   │   └── user.py          # User model
│   └── utils/
│       ├── __init__.py
│       ├── keyboards.py     # Inline keyboard layouts
│       └── helpers.py       # Helper functions
├── data/                    # Database storage
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Development

To contribute or modify the bot:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for your business needs.

## Support

For issues or questions, please open an issue on the repository.
