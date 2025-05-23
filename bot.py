from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from flask import Flask

# ========== Flask сервер для тестирования ==========
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Бот работает. Это тестовая страница."

def run_flask():
    flask_app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000))

# ========== Telegram-бот ==========
TOKEN = '8159127478:AAHwjKl3zeZ3LZ4RgJgZ9X4Y1WOOKQFyZww'

products = [
    {
        "id": "1",
        "name": "Деревянный стул",
        "description": "Эргономичный стул ручной работы из натурального дерева.",
        "dimensions": "50x50x85 см",
        "material": "Массив дуба",
        "production_time": "7 дней",
        "advantages": "Экологичность, прочность, долговечность",
        "price": "5500 руб."
    },
    {
        "id": "2",
        "name": "Чехол для iPhone",
        "description": "Защитный чехол с уникальным дизайном и амортизацией.",
        "dimensions": "16x9x1 см",
        "material": "ТПУ + поликарбонат",
        "production_time": "3 дня",
        "advantages": "Лёгкий, ударопрочный, стильный",
        "price": "990 руб."
    }
]

def product_message(product):
    return (f"📦 <b>{product['name']}</b>\n\n"
            f"📝 <i>{product['description']}</i>\n\n"
            f"📏 Габариты: {product['dimensions']}\n"
            f"🧱 Материал: {product['material']}\n"
            f"⏳ Срок изготовления: {product['production_time']}\n"
            f"✅ Преимущества: {product['advantages']}\n"
            f"💰 Цена: {product['price']}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(product["name"], callback_data=product["id"])] for product in products]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🛒 Выберите товар:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = query.data
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        await query.edit_message_text(text=product_message(product), parse_mode="HTML")

if __name__ == '__main__':
    from threading import Thread
    Thread(target=run_flask).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот и Flask-сервер успешно запущены")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8000)),
        url_path=TOKEN,
        webhook_url=f"https://metalfencingbot-6.onrender.com/ {TOKEN}"
    )
