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

# ========== ДАННЫЕ О ТОВАРАХ (упрощенная версия из ТЗ) ==========
categories = [
    {"id": "1", "name": "Снегозадержатели"},
    {"id": "2", "name": "Кровельные ограждения"},
    {"id": "3", "name": "Пожарные лестницы"},
    {"id": "4", "name": "Лестницы"},
    {"id": "5", "name": "Переходные мостики"}
]

products = {
    "1": [
        {
            "id": "1_1",
            "name": "СТС «ПРОФ»",
            "description": "Снегозадержатель для кровель из профнастила и сэндвич-панелей.",
            "specs": ["Кровля из сэндвич панели", "Кровля из профнастила высокой волны"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 3475, "Цинк+краска": 3735},
            "photo": "СТС «ПРОФ».jpg"
        },
        # Остальные товары из категории...
    ],
    # Остальные категории...
}

# Глобальные переменные для хранения состояния
user_carts = {}  # Корзины пользователей
user_states = {}  # Текущие состояния пользователей

# ========== ФОРМАТИРОВАНИЕ СООБЩЕНИЙ ==========
def format_product_message(product, selected_options=None):
    message = f"📦 <b>{product['name']}</b>\n\n"
    message += f"📝 <i>{product['description']}</i>\n\n"
    
    if selected_options:
        for option, value in selected_options.items():
            message += f"🔹 {option}: {value}\n"
    
    if 'price' in product:
        if isinstance(product['price'], dict):
            message += "\n💰 Цены:\n"
            for coating, price in product['price'].items():
                message += f"  • {coating}: {price} руб./шт\n"
        else:
            message += f"💰 Цена: {product['price']} руб./шт\n"
    
    return message

# ========== ОСНОВНЫЕ КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_carts[user_id] = []  # Инициализация корзины
    user_states[user_id] = "MAIN_MENU"  # Установка состояния
    
    keyboard = [
        [InlineKeyboardButton("🏢 О компании", callback_data="about")],
        [InlineKeyboardButton("📚 Каталог", callback_data="catalog")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "👋 Вас приветствует официальный бот продаж продукции ООО «СТС»!\n\n"
        "Мы предлагаем элементы безопасности на ВСЕ типы кровель, цены завода изготовителя, "
        "отгрузка от 1 дня. Воспользуйтесь нашим онлайн-решением для удобного "
        "формирования заявок на покупку продукции!"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def about_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    about_text = (
        "🏢 <b>О компании</b>\n\n"
        "Компания ООО «СТС» работает в области производства элементов безопасности кровли с 2014 года.\n\n"
        "Мы применяем высокоточные станки, а на нашем производстве задействованы специалисты с опытом от 5 лет.\n\n"
        "Мы осуществляем бесплатную доставку до терминала транспортной компании в вашем городе.\n\n"
        "🌐 Официальный сайт: <a href='http://эбк-стс.рф'>эбк-стс.рф</a>"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode="HTML")

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    contacts_text = (
        "📞 <b>Контакты</b>\n\n"
        "Наш e-mail: ctcnet@yandex.ru\n\n"
        "Задайте вопрос, и мы свяжемся с вами в ближайшее время!"
    )
    
    keyboard = [
        [InlineKeyboardButton("📩 Задать вопрос", callback_data="ask_question")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(contacts_text, reply_markup=reply_markup, parse_mode="HTML")

# ========== КАТАЛОГ И КОРЗИНА ==========
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(cat["name"], callback_data=f"cat_{cat['id']}")]
        for cat in categories
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📚 <b>Каталог продукции</b>\n\nВыберите категорию:", 
                                reply_markup=reply_markup, 
                                parse_mode="HTML")

async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_id = query.data.split("_")[1]
    
    if category_id not in products:
        await query.edit_message_text("⚠️ Товары в этой категории временно отсутствуют.")
        return
    
    keyboard = [
        [InlineKeyboardButton(product["name"], callback_data=f"prod_{product['id']}")]
        for product in products[category_id]
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="catalog")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"🏷 <b>{categories[int(category_id)-1]['name']}</b>\n\nВыберите модель:", 
                                reply_markup=reply_markup, 
                                parse_mode="HTML")

# ========== ОБРАБОТЧИКИ СООБЩЕНИЙ ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    current_state = user_states.get(user_id, "MAIN_MENU")
    
    if current_state == "AWAITING_QUESTION":
        question = update.message.text
        await send_question_to_admin(update, context, question)
        user_states[user_id] = "MAIN_MENU"
        
        keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📩 Ваш вопрос отправлен! Мы свяжемся с вами в ближайшее время.",
            reply_markup=reply_markup
        )

async def send_question_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, question):
    user = update.effective_user
    message = (
        f"❓ <b>Новый вопрос от пользователя</b>\n\n"
        f"👤 Пользователь: {user.full_name}\n"
        f"📱 Телефон: {user.id}\n\n"
        f"📝 Вопрос:\n{question}"
    )
    
    for admin_id in ADMIN_CHAT_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке вопроса администратору {admin_id}: {e}")

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

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
