from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 8000))
TOKEN = '8159127478:AAHwjKl3zeZ3LZ4RgJgZ9X4Y1WOOKQFyZww'
ADMIN_CHAT_IDS = ['79100904945', '79032587332']  # ID менеджера и администратора

# Данные о товарах
products = [
    {
        "id": "sts_prof",
        "name": "СТС «ПРОФ»",
        "description": (
            "Снегозадержатель СТС «ПРОФ» длиной 3000 мм предназначен для кровель из профнастила выше НС40 и "
            "сэндвич-панели любого производителя.\n\n"
            "Соответствует требованиям ГОСТ.\n\n"
            "Комплектация:\n"
            "• Труба плоскоовал Zn 45×25 – 2 шт.\n"
            "• Кронштейн усиленный СТС с герметичной бутило-каучуковой лентой, оцинкованный, толщина металла 2 мм – 4 шт.\n"
            "• Заглушки 45х25 – 4 шт."
        ),
        "specs": ["Кровля из сэндвич панели", "Кровля из профнастила высокой волны"],
        "coatings": ["Цинк", "Цинк+краска"],
        "colors": {
            "RAL 3003": "Рубиново-красный",
            "RAL 3005": "Винно-красный",
            "RAL 5005": "Сигнальный синий",
            "RAL 6005": "Зеленый мох",
            "RAL 7004": "Серый",
            "RAL 8017": "Коричневый",
            "RAL 9003": "Белый"
        },
        "prices": {
            "Цинк": 3475,
            "Цинк+краска": 3735
        }
    }
]

# Функции для формирования сообщений
def format_product_info(product_id, user_id):
    product = next(p for p in products if p["id"] == product_id)
    data = user_data.get(user_id, {})
    
    text = f"<b>{product['name']}</b>\n\n"
    text += f"<i>Описание:</i>\n{product['description']}\n\n"
    
    if "spec" in data:
        text += f"<i>Спецификация:</i> {data['spec']}\n"
    
    if "coating" in data:
        text += f"<i>Покрытие:</i> {data['coating']}\n"
        if data['coating'] == "Цинк+краска" and "color" in data:
            text += f"<i>Цвет (RAL):</i> {data['color']}\n"
    
    if "quantity" in data and "coating" in data:
        price = product['prices'][data['coating']]
        total = price * data['quantity']
        text += f"\n<i>Цена:</i> {price} руб./шт.\n"
        text += f"<i>Количество:</i> {data['quantity']} шт.\n"
        text += f"<b>Итого:</b> {total} руб."
    
    return text

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(product["name"], callback_data=f"product_{product['id']}")] 
               for product in products]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🛒 Выберите товар:", reply_markup=reply_markup)

async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    product_id = query.data.split("_")[1]
    user_id = query.from_user.id
    user_data[user_id] = {"product_id": product_id}
    
    product = next(p for p in products if p["id"] == product_id)
    
    # Отправляем описание
    await query.edit_message_text(
        text=format_product_info(product_id, user_id),
        parse_mode="HTML"
    )
    
    # Предлагаем выбрать спецификацию
    keyboard = [[InlineKeyboardButton(spec, callback_data=f"spec_{spec}")] for spec in product["specs"]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Выберите спецификацию:",
        reply_markup=reply_markup
    )

async def handle_spec_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    spec = query.data.split("_")[1]
    user_id = query.from_user.id
    user_data[user_id]["spec"] = spec
    
    product_id = user_data[user_id]["product_id"]
    product = next(p for p in products if p["id"] == product_id)
    
    # Предлагаем выбрать покрытие
    keyboard = [[InlineKeyboardButton(coating, callback_data=f"coating_{coating}")] 
               for coating in product["coatings"]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=format_product_info(product_id, user_id),
        parse_mode="HTML"
    )
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Выберите защитное покрытие:",
        reply_markup=reply_markup
    )

async def handle_coating_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    coating = query.data.split("_")[1]
    user_id = query.from_user.id
    user_data[user_id]["coating"] = coating
    
    product_id = user_data[user_id]["product_id"]
    product = next(p for p in products if p["id"] == product_id)
    
    if coating == "Цинк+краска":
        # Предлагаем выбрать цвет
        colors = list(product["colors"].items())
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"color_{code}") for code, name in colors[i:i+2]]
            for i in range(0, len(colors), 2)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=format_product_info(product_id, user_id),
            parse_mode="HTML"
        )
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Выберите цвет (RAL Classic):",
            reply_markup=reply_markup
        )
    else:
        # Пропускаем выбор цвета, переходим к количеству
        await query.edit_message_text(
            text=format_product_info(product_id, user_id),
            parse_mode="HTML"
        )
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Введите количество (шт.):",
            reply_markup=None
        )

async def handle_color_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    color_code = query.data.split("_")[1]
    user_id = query.from_user.id
    user_data[user_id]["color"] = f"{color_code} ({products[0]['colors'][color_code]})"
    
    product_id = user_data[user_id]["product_id"]
    await query.edit_message_text(
        text=format_product_info(product_id, user_id),
        parse_mode="HTML"
    )
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Введите количество (шт.):",
        reply_markup=None
    )

async def handle_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        quantity = int(update.message.text)
        if quantity <= 0:
            raise ValueError
        
        user_data[user_id]["quantity"] = quantity
        product_id = user_data[user_id]["product_id"]
        
        await update.message.reply_text(
            text=format_product_info(product_id, user_id),
            parse_mode="HTML"
        )
        
        # Предлагаем оформить заказ
        keyboard = [[InlineKeyboardButton("Оформить заказ", callback_data="order")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text="Для оформления заказа нажмите кнопку ниже:",
            reply_markup=reply_markup
        )
        
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное количество (целое число больше 0):")

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in user_data or "quantity" not in user_data[user_id]:
        await query.edit_message_text("Ошибка: данные заказа не найдены")
        return
    
    product_id = user_data[user_id]["product_id"]
    product = next(p for p in products if p["id"] == product_id)
    
    # Здесь можно добавить логику оформления заказа
    await query.edit_message_text(
        text=f"✅ Ваш заказ оформлен!\n\n{format_product_info(product_id, user_id)}",
        parse_mode="HTML"
    )
    
    # Очищаем данные пользователя
    user_data.pop(user_id, None)

# Flask приложение
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Бот работает! Используйте Telegram для взаимодействия."

@flask_app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put(update)
    return 'ok'

# ========== ЗАПУСК БОТА ==========
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    
    # Обработчики callback-запросов
    app.add_handler(CallbackQueryHandler(about_company, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(contacts, pattern="^contacts$"))
    app.add_handler(CallbackQueryHandler(show_catalog, pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    app.add_handler(CallbackQueryHandler(show_category_products, pattern="^cat_"))
    
    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск через Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://metalfencingbot.onrender.com/{TOKEN}"
    )

if __name__ == '__main__':
    main()
