# Google Sheets Setup Guide

This guide will help you set up Google Sheets as the database for your BeanLeaf POS bot.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- Your Telegram bot already set up

## Step 1: Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it "BeanLeaf POS Database" (or your preferred name)
4. Copy the **Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
   ```
   Save this ID for later.

## Step 2: Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Sheets API
   - Google Drive API
   
   To enable:
   - Click "Enable APIs and Services"
   - Search for each API
   - Click "Enable"

## Step 3: Create Service Account

1. In Google Cloud Console, go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Name it "beanleaf-pos-bot" (or your preferred name)
4. Click **Create and Continue**
5. Grant role: **Editor**
6. Click **Done**

## Step 4: Create and Download Credentials

1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Choose **JSON** format
5. Click **Create**
6. The JSON file will download automatically
7. Rename it to `credentials.json`
8. Move it to your project root directory (same level as bot/ folder)

## Step 5: Share the Google Sheet

1. Open your Google Sheet
2. Click the **Share** button (top right)
3. Copy the **email address** from your `credentials.json` file:
   ```json
   {
     "client_email": "beanleaf-pos-bot@projectname.iam.gserviceaccount.com",
     ...
   }
   ```
4. Paste this email in the Share dialog
5. Give **Editor** permissions
6. Uncheck "Notify people"
7. Click **Share**

## Step 6: Configure Environment Variables

1. Open your `.env` file
2. Add your configuration:
   ```
   BOT_TOKEN=your_telegram_bot_token
   GOOGLE_SHEET_ID=your_spreadsheet_id_from_step_1
   GOOGLE_CREDENTIALS_FILE=credentials.json
   ADMIN_USER_ID=your_telegram_user_id
   ```

## Step 7: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 8: Run the Bot

```bash
python bot/main.py
```

On first run, the bot will automatically create the following worksheets in your Google Sheet:
- **Users** - Stores user information
- **Products** - Product catalog
- **Orders** - Order history
- **OrderItems** - Individual items in each order

## Troubleshooting

### "Credentials file not found"
- Make sure `credentials.json` is in the project root
- Check the path in your `.env` file

### "Failed to authenticate with Google Sheets"
- Verify that the Google Sheets API and Google Drive API are enabled
- Check that you've shared the spreadsheet with the service account email
- Ensure the credentials file is valid JSON

### "Permission denied"
- Make sure the service account has Editor access to the spreadsheet
- Check that the GOOGLE_SHEET_ID in `.env` matches your spreadsheet

## Benefits of Using Google Sheets

✅ **Real-time Access**: View and edit data directly in the spreadsheet  
✅ **Easy Backup**: Built-in version history and automatic backups  
✅ **Collaboration**: Multiple people can view/manage data  
✅ **No Database Server**: No need to set up or maintain a database  
✅ **Visual Interface**: See your data in a familiar spreadsheet format  
✅ **Data Analysis**: Use Google Sheets formulas and charts  

## Sheet Structure

### Users
| id | telegram_id | username | first_name | last_name | is_admin | created_at |
|----|-------------|----------|------------|-----------|----------|------------|

### Products
| id | name | description | price | stock | is_available | created_at | updated_at |
|----|------|-------------|-------|-------|--------------|------------|------------|

### Orders
| id | user_id | total_amount | status | created_at | completed_at |
|----|---------|--------------|--------|------------|--------------|

### OrderItems
| id | order_id | product_id | product_name | quantity | price | subtotal |
|----|----------|------------|--------------|----------|-------|----------|

## Managing Data

You can directly edit the Google Sheet to:
- Add/edit products
- Update stock levels
- View orders and sales
- Manage user permissions
- Generate reports using Google Sheets features

**Important**: Be careful when editing IDs, as they need to remain unique integers.
