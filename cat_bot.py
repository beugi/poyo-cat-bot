import os
import asyncio
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CAT STATUS ---
cat_status = "Unknown"
last_updated = "Never"

# --- MEAL TRACKER ---
meal_status = {
    "breakfast": False,
    "dinner": False,
    "last_updated": date.today()
}

def format_meal_status():
    today = date.today()
    if meal_status["last_updated"] != today:
        meal_status["breakfast"] = False
        meal_status["dinner"] = False
        meal_status["last_updated"] = today

    b = "✅ Breakfast" if meal_status["breakfast"] else "⬜ Breakfast"
    d = "✅ Dinner" if meal_status["dinner"] else "⬜ Dinner"
    return f"🥣 Meal log for {today.strftime('%b %d')}:\n{b}\n{d}"

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📡 Chat ID is:", update.effective_chat.id)
    keyboard = [[
        InlineKeyboardButton("INSIDE", callback_data="INSIDE"),
        InlineKeyboardButton("OUTSIDE", callback_data="OUTSIDE")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🐱 The cat is currently: {cat_status}\nLast updated: {last_updated}",
        reply_markup=reply_markup
    )

# --- /meals ---
async def meals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("Ate Breakfast", callback_data="meal_breakfast"),
        InlineKeyboardButton("Ate Dinner", callback_data="meal_dinner")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        format_meal_status(),
        reply_markup=reply_markup
    )

# --- Button Handler ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cat_status, last_updated

    query = update.callback_query
    await query.answer()

    if query.data in ["INSIDE", "OUTSIDE"]:
        cat_status = query.data
        user = query.from_user.first_name or query.from_user.username or "Someone"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_updated = f"{cat_status} by {user} at {timestamp}"

        keyboard = [[
            InlineKeyboardButton("INSIDE", callback_data="INSIDE"),
            InlineKeyboardButton("OUTSIDE", callback_data="OUTSIDE")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"🐱 POYO is: {cat_status}\nLast updated: {last_updated}",
            reply_markup=reply_markup
        )

        await query.edit_message_reply_markup(reply_markup=None)

    elif query.data.startswith("meal_"):
        if query.data == "meal_breakfast":
            meal_status["breakfast"] = True
        elif query.data == "meal_dinner":
            meal_status["dinner"] = True

        keyboard = [[
            InlineKeyboardButton("Ate Breakfast", callback_data="meal_breakfast"),
            InlineKeyboardButton("Ate Dinner", callback_data="meal_dinner")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=format_meal_status(),
            reply_markup=reply_markup
        )

        await query.edit_message_reply_markup(reply_markup=None)

# --- Daily Reset Task ---
async def daily_reset():
    while True:
        now = datetime.now()
        # Calculate next 6:00 AM
        tomorrow = now.date() + timedelta(days=1)
        next_6am = datetime.combine(tomorrow, datetime.min.time()).replace(hour=6)
        wait_seconds = (next_6am - now).total_seconds()
        
        await asyncio.sleep(wait_seconds)

        # Reset meal tracker
        meal_status["breakfast"] = False
        meal_status["dinner"] = False
        meal_status["last_updated"] = date.today()
        print("✅ Meal tracker reset and reminder sent at 6 AM.")

        # Broadcast to your main chat (replace CHAT_ID with actual chat ID)
        try:
            keyboard = [[
                InlineKeyboardButton("Ate Breakfast", callback_data="meal_breakfast"),
                InlineKeyboardButton("Ate Dinner", callback_data="meal_dinner")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await app.bot.send_message(
                chat_id=os.getenv("CHAT_ID"),  # You must set this env variable
                text=format_meal_status(),
                reply_markup=reply_markup
            )
        except Exception as e:
            print("⚠️ Could not send daily /meals message:", e)

# --- Run the Bot ---
TOKEN = os.getenv("BOT_TOKEN")
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("meals", meals))
app.add_handler(CallbackQueryHandler(button_handler))

async def main():
    await asyncio.gather(
        app.run_polling(),
        daily_reset()
    )

# ✅ Railway-compatible (works with existing event loop)
if __name__ == "__main__":
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        print("⚠️ nest_asyncio not found. Be sure to install it: pip install nest_asyncio")

    asyncio.get_event_loop().run_until_complete(main())
