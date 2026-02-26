from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import os

TOKEN = os.getenv("BOT_TOKEN")

TAX_RATE = 0.0625
REGISTRATION_FEE = 431

keyboard = ReplyKeyboardMarkup(
    [
        ["Enter Vehicle Price"],
        ["Enter Total (Out-the-Door)"],
    ],
    resize_keyboard=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Choose calculation type:",
        reply_markup=keyboard,
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Enter Vehicle Price":
        context.user_data["mode"] = "price"
        await update.message.reply_text("Enter vehicle price:")
    elif text == "Enter Total (Out-the-Door)":
        context.user_data["mode"] = "total"
        await update.message.reply_text("Enter total amount:")

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("$", "").replace(",", "").strip()
        value = float(text)
        mode = context.user_data.get("mode")

        if mode == "price":
            price = value
            tax = price * TAX_RATE
            total = price + tax + REGISTRATION_FEE
        elif mode == "total":
            total = value
            price = (total - REGISTRATION_FEE) / (1 + TAX_RATE)
            tax = price * TAX_RATE
        else:
            await update.message.reply_text("Press a button first.", reply_markup=keyboard)
            return

        response = (
            f"Vehicle Price: ${price:,.2f}\n"
            f"Sales Tax (6.25%): ${tax:,.2f}\n"
            f"Registration Fee: ${REGISTRATION_FEE:,.2f}\n"
            f"Total: ${total:,.2f}"
        )

        await update.message.reply_text(response, reply_markup=keyboard)

    except ValueError:
        await update.message.reply_text("Enter a valid number.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Regex("^(Enter Vehicle Price|Enter Total \\(Out-the-Door\\))$"), handle_buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

app.run_polling()
