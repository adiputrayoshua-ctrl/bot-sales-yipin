python
import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "telegram-sales-bot-482415-49dbbe785923.json", scope
)
client = gspread.authorize(creds)
sheet = client.open("Laporan Sales Outlet").sheet1

def load_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def get_sales(outlet):
    df = load_data()
    f = df[df["Outlet"] == outlet]

    if f.empty:
        return "❌ Data tidak ditemukan."

    return f"""
📊 *Laporan Sales*
🏪 *{outlet}*

💰 Gross: Rp{int(f['Gross Sales'].sum()):,}
💵 Net: Rp{int(f['Net Sales'].sum()):,}
🧾 Transaksi: {int(f['Transaksi'].sum())}
"""

async def start(update: Update, context):
    df = load_data()
    outlets = df["Outlet"].unique()

    keyboard = [
        [InlineKeyboardButton(o, callback_data=o)]
        for o in outlets
    ]

    await update.message.reply_text(
        "Pilih outlet:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context):
    query = update.callback_query
    await query.answer()
    result = get_sales(query.data)
    await query.edit_message_text(
        text=result,
        parse_mode="Markdown"
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
