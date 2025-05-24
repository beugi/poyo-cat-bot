import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime

cat_status = "Unknown"
last_updated = "Never"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("INSIDE", callback_data="INSIDE"),
        InlineKeyboardButton("OUTSIDE", callback_data="OUTSIDE")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🐱 The cat is currently: {cat_status}\nLast updated: {last_updated}",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cat_status, last_updated

    query = update.callback_query
    await query.answer()

    cat_status = query.data

    user = query.from_user.first_name or query.from_user.username or "Someone"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_updated = f"{cat_status} by {user} at {timestamp}"

    keyboard = [[
        InlineKeyboardButton("INSIDE", callback_data="INSIDE"),
        InlineKeyboardButton("OUTSIDE", callback_data="OUTSIDE")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 1. Send new message with updated status and buttons
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"🐱 POYO is: {cat_status}\nLast updated: {last_updated}",
        reply_markup=reply_markup
    )

    # 2. Remove buttons from the previous message
    await query.edit_message_reply_markup(reply_markup=None)

# ⬇️ Replace this with your actual token
TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
