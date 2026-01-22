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

- Node.js 18.x or higher
- TypeScript 5.x
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Google account with access to Google Sheets

## Quick Start

### 1. Clone the repository
```bash
cd beanleafPOS
```

### 2. Install dependencies
```bash
npm install
```

### 3. Set up Google Sheets (IMPORTANT!)

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

### 4. Configure environment variables
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

### 5. Build the project
```bash
npm run build
```

### 6. Run the bot
```bash
npm start
```

Or for development with auto-reload:
```bash
npm run dev
```

The bot will automatically create necessary worksheets in your Google Sheet on first run!

## Usage

### Customer Commands
- `/start` - Start the bot and view main menu
- Browse available products
- View your shopping cart
- Complete your order

### Admin Commands
- Access admin panel
- Add/edit products
- Manage order queue
- View sales statistics

## Project Structure

```
beanleafPOS/
├── src/
│   ├── main.ts              # Main bot application
│   ├── handlers/
│   │   ├── index.ts
│   │   ├── admin.ts         # Admin command handlers
│   │   ├── customer.ts      # Customer command handlers
│   │   └── orders.ts        # Order processing handlers
│   ├── models/
│   │   ├── index.ts
│   │   ├── database.ts      # Database setup
│   │   ├── product.ts       # Product model
│   │   ├── order.ts         # Order model
│   │   └── user.ts          # User model
│   └── utils/
│       ├── index.ts
│       ├── keyboards.ts     # Inline keyboard layouts
│       └── helpers.ts       # Helper functions
├── dist/                    # Compiled JavaScript
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
└── README.md
```

## Development

To contribute or modify the bot:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `npm run dev`
5. Build with `npm run build`
6. Submit a pull request

## Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm start` - Run the compiled bot
- `npm run dev` - Run in development mode with ts-node
- `npm run watch` - Watch for changes and recompile

## License

MIT License - feel free to use this project for your business needs.

## Support

For issues or questions, please open an issue on the repository.
