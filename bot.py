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

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 8000))
TOKEN = '8159127478:AAHwjKl3zeZ3LZ4RgJgZ9X4Y1WOOKQFyZww'
ADMIN_CHAT_IDS = ['79100904945', '79032587332']

# ========== ДАННЫЕ О ТОВАРАХ ==========
categories = [
    {"id": "1", "name": "❄ Снегозадержатели"},
    {"id": "2", "name": "🪜 Кровельные ограждения"},
    {"id": "3", "name": "🔥 Пожарные лестницы"},
    {"id": "4", "name": "🪜 Лестницы"},
    {"id": "5", "name": "🌉 Переходные мостики"}
]

products = {
    "1": [
        {
            "id": "1_1",
            "name": "СТС «ПРОФ»",
            "description": (
                "Снегозадержатель СТС «ПРОФ» длиной 3000 мм предназначен для кровель из профнастила выше НС40 и сендвич-панели любого производителя.\n"
                "Снегозадержатель соответствует требованиям ГОСТ.\n"
                "Комплектация:\n"
                "1. Труба плоскоовал Zn 45×25 – 2 шт.\n"
                "2. Кронштейн усиленный СТС с герметичной бутило-каучуковой лентой, оцинкованный, толщина металла 2 мм – 4 шт.\n"
                "3. Заглушки 45х25 – 4 шт."
            ),
            "specs": ["Кровля из сэндвич панели", "Кровля из профнастила высокой волны"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 3475, "Цинк+краска": 3735},
            "photo": "СТС «ПРОФ».jpg"
        },
        {
            "id": "1_2",
            "name": "СТС «Универсальный усиленный»",
            "description": (
                "Снегозадержатель СТС «Универсальный усиленный» длиной 3000 мм подходит для всех видов кровельных материалов.\n"
                "Имеет улучшенную конструкцию из усиленного кронштейна и плоскоовальной трубы, что позволяет выдерживать большие нагрузки.\n"
                "Толщина металла трубы не менее 1,5 мм, кронштейна — 2 мм."
            ),
            "specs": ["Нет вариантов"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 2805, "Цинк+краска": 3100},
            "photo": "СТС «Усиленный универсальный».jpg"
        }
    ],
    # Здесь можно добавить другие категории по аналогии
}

# Хранение состояния пользователей
user_carts = {}
user_states = {}
user_selections = {}

# ========== ОСНОВНОЕ МЕНЮ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_carts[user_id] = []
    user_states[user_id] = "MAIN_MENU"
    user_selections[user_id] = {}

    keyboard = [
        [InlineKeyboardButton("🏢 О компании", callback_data="about")],
        [InlineKeyboardButton("🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "👋 Вас приветствует официальный бот продаж продукции ООО «СТС»!\n\n"
        "Мы предлагаем элементы безопасности на ВСЕ типы кровель, цены завода изготовителя, отгрузка от 1 дня.\n"
        "Воспользуйтесь нашим онлайн-решением для удобного формирования заявок!"
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")

# ========== О КОМПАНИИ ==========
async def about_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🏛 <b>О компании</b>\n\n"
        "Компания ООО «СТС» работает в области производства элементов безопасности кровли с 2014 года.\n"
        "На нашем производстве задействованы специалисты с опытом более 5 лет.\n"
        "Мы осуществляем бесплатную доставку до терминала ТК в вашем городе.\n"
        "🔗 Официальный сайт: <a href='https://эбк-стс.рф'>эбк-стс.рф</a>" 
    )
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

# ========== КОНТАКТЫ ==========
async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📞 <b>Контакты</b>\n\n"
        "📧 e-mail: ctcnet@yandex.ru\n\n"
        "💬 Напишите свой вопрос:"
    )
    keyboard = [
        [InlineKeyboardButton("💬 Задать вопрос", callback_data="ask_question")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

# ========== КАТАЛОГ ==========
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    user_states[user_id] = "CATALOG"

    keyboard = [[InlineKeyboardButton(cat["name"], callback_data=f"cat_{cat['id']}")] for cat in categories]
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📚 Выберите категорию:", reply_markup=reply_markup)

# ========== ПРОДУКТЫ ПО КАТЕГОРИЯМ ==========
async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_id = query.data.split("_")[1]
    user_id = str(query.from_user.id)
    user_states[user_id] = f"CATEGORY_{category_id}"

    if category_id not in products or len(products[category_id]) == 0:
        await query.edit_message_text("⚠️ Товары временно отсутствуют.")
        return

    keyboard = [[InlineKeyboardButton(product["name"], callback_data=f"prod_{product['id']}")] for product in products[category_id]]
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"🏷 Выберите модель {categories[int(category_id)-1]['name']}:", 
                                reply_markup=reply_markup, parse_mode="HTML")

# ========== ПОКАЗ ПРОДУКТА ==========
async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[1]
    user_id = str(query.from_user.id)

    found = False
    for cat in products.values():
        for p in cat:
            if p["id"] == product_id:
                found = True
                user_selections[user_id] = {
                    "product_id": product_id,
                    "product": p,
                    "selected_options": {}
                }
                user_states[user_id] = f"PRODUCT_{product_id}"

                keyboard = []
                if p.get("specs") and p["specs"][0] != "Нет вариантов":
                    keyboard.append([InlineKeyboardButton("📌 Спецификация", callback_data=f"spec_{product_id}")])

                if p.get("heights"):
                    keyboard.append([InlineKeyboardButton("📐 Высота", callback_data=f"height_{product_id}")])

                if p.get("cross_tubes"):
                    keyboard.append([InlineKeyboardButton("🔧 Кол-во труб", callback_data=f"tube_{product_id}")])

                keyboard.append([InlineKeyboardButton("🎨 Защитное покрытие", callback_data=f"coating_{product_id}")])
                keyboard.append([InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"add_cart_{product_id}")])
                keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"cat_{category_id}")])

                reply_markup = InlineKeyboardMarkup(keyboard)
                message = format_product_message(p)
                await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
                photo_path = p.get("photo", "")
                if photo_path:
                    with open(photo_path, "rb") as photo:
                        await context.bot.send_photo(chat_id=query.message.chat_id, photo=photo)
                break

    if not found:
        await query.edit_message_text("⚠️ Товар не найден.")

# ========== ВЫБОР ПОКРЫТИЯ ==========
async def handle_coating_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, product_id = query.data.split("_")[1:]
    user_id = str(query.from_user.id)

    product = None
    for cat in products.values():
        for p in cat:
            if p["id"] == product_id:
                product = p
                break
        if product:
            break

    if not product:
        await query.edit_message_text("⚠️ Продукт не найден.")

    keyboard = [[InlineKeyboardButton(coat, callback_data=f"select_coating_{product_id}_{i}")]
                for i, coat in enumerate(product["coating"])]
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"prod_{product_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🛡 Выберите защитное покрытие:", reply_markup=reply_markup)

# ========== ОБРАБОТЧИК ВЫБОРА ПОКРЫТИЯ ==========
async def select_coating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, product_id, index = query.data.split("_")[1:]
    user_id = str(query.from_user.id)
    index = int(index)

    product = None
    for cat in products.values():
        for p in cat:
            if p["id"] == product_id:
                product = p
                break
        if product:
            break

    if not product:
        await query.edit_message_text("⚠️ Продукт не найден.")
        return

    selected_coating = product["coating"][index]
    user_selections[user_id]["selected_options"]["Защитное покрытие"] = selected_coating

    if selected_coating == "Цинк+краска":
        keyboard = [
            [InlineKeyboardButton("🎨 Указать цвет RAL", callback_data=f"enter_ral_{product_id}")],
            [InlineKeyboardButton("⬅️ Назад", callback_data=f"coating_{product_id}")]
        ]
        await query.edit_message_text(
            "🎨 Вы выбрали Цинк+краска. Пожалуйста, укажите цвет по каталогу RAL Classic (четырехзначное число):",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await select_quantity(update, context, product_id)

# ========== ВВОД RAL ЦВЕТА ==========
async def enter_ral_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, product_id = query.data.split("_")
    user_id = str(update.effective_user.id)
    user_states[user_id] = f"AWAITING_RAL_{product_id}"
    await query.edit_message_text("✏️ Введите четырехзначный код RAL (например, 3005):")

# ========== ВВОД КОЛИЧЕСТВА ==========
async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id=None):
    if product_id is None:
        _, product_id = update.callback_query.data.split("_")[1:]

    user_id = str(update.effective_user.id)
    user_states[user_id] = f"AWAITING_QUANTITY_{product_id}"

    await update.callback_query.edit_message_text("🔢 Введите количество штук:")

# ========== ОБРАБОТЧИК ВВОДА КОЛИЧЕСТВА ==========
async def handle_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    current_state = user_states.get(user_id, "")

    if not current_state.startswith("AWAITING_QUANTITY_"):
        return

    product_id = current_state.split("_")[2]
    try:
        quantity = int(update.message.text)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ Введите целое положительное число:")
        return

    product = user_selections[user_id]["product"]
    coating = user_selections[user_id]["selected_options"].get("Защитное покрытие", "")
    price_per_item = product["price"].get(coating, 0) if coating else list(product["price"].values())[0]
    total_price = price_per_item * quantity
    user_selections[user_id]["selected_options"]["Количество"] = quantity
    user_selections[user_id]["selected_options"]["Итоговая цена"] = total_price

    summary = format_product_message(product, user_selections[user_id]["selected_options"])
    keyboard = [
        [InlineKeyboardButton("✅ Добавить в корзину", callback_data=f"confirm_add_{product_id}")],
        [InlineKeyboardButton("🔄 Изменить количество", callback_data=f"prod_{product_id}")]
    ]

    await update.message.reply_text(summary + f"\n💰 Общая сумма: {total_price} руб.", 
                                    reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

# ========== ДОБАВЛЕНИЕ В КОРЗИНУ ==========
async def confirm_add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[2]
    user_id = str(query.from_user.id)

    cart_item = {
        "product": user_selections[user_id]["product"],
        "selected_options": user_selections[user_id]["selected_options"].copy()
    }

    if user_id not in user_carts:
        user_carts[user_id] = []

    user_carts[user_id].append(cart_item)
    user_states[user_id] = "IN_CART"

    keyboard = [
        [InlineKeyboardButton("📥 Сформировать заявку", callback_data="form_order")],
        [InlineKeyboardButton("🛒 Продолжить покупки", callback_data="catalog")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("✅ Товар успешно добавлен в корзину!", reply_markup=reply_markup)

# ========== ФОРМА ЗАЯВКИ ==========
async def form_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    user_states[user_id] = "ORDER_FORM_NAME"
    await query.edit_message_text("👤 Введите ваше имя:")

# ========== ОБРАБОТЧИК СООБЩЕНИЙ ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    current_state = user_states.get(user_id, "")

    if current_state.startswith("AWAITING_RAL_"):
        product_id = current_state.split("_")[2]
        ral_code = update.message.text.strip()

        if not (ral_code.isdigit() and len(ral_code) == 4):
            await update.message.reply_text("⚠️ Введите корректный код RAL (4 цифры):")
            return

        user_selections[user_id]["selected_options"]["Цвет, RAL Classic"] = f"RAL {ral_code}"
        await select_quantity(update, context, product_id)

    elif current_state.startswith("AWAITING_QUANTITY_"):
        await handle_quantity_input(update, context)

    elif current_state == "AWAITING_QUESTION":
        question = update.message.text
        await send_question_to_admin(update, context, question)

# ========== ЗАДАТЬ ВОПРОС ==========
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    user_states[user_id] = "AWAITING_QUESTION"
    await query.edit_message_text("✍️ Введите ваш вопрос:")

# ========== ОТПРАВКА ВОПРОСА АДМИНАМ ==========
async def send_question_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, question):
    user = update.effective_user
    message = (
        f"❓ <b>Новый вопрос от пользователя:</b>\n\n"
        f"👤 Имя: {user.full_name}\n"
        f"📱 ID: {user.id}\n"
        f"📝 Вопрос: {question}"
    )
    for admin_id in ADMIN_CHAT_IDS:
        await context.bot.send_message(chat_id=admin_id, text=message, parse_mode="HTML")

    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="contacts")]]
    await update.message.reply_text("✅ Ваш вопрос отправлен!", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def format_product_message(product, selected_options=None):
    message = f"📦 <b>{product['name']}</b>\n\n"
    message += f"📝 {product['description']}\n\n"
    
    if selected_options:
        for option, value in selected_options.items():
            message += f"🔹 {option}: {value}\n"
    
    message += "💰 Цена: "
    if isinstance(product['price'], dict):
        for coating, price in product['price'].items():
            message += f"{coating} — {price} руб./шт\n"
    else:
        message += f"{product['price']} руб./шт\n"

    return message

# ========== ВЕРНУТЬСЯ В МЕНЮ ==========
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# ========== ЗАПУСК БОТА ==========
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(about_company, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(contacts, pattern="^contacts$"))
    app.add_handler(CallbackQueryHandler(show_catalog, pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    app.add_handler(CallbackQueryHandler(show_category_products, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(show_product, pattern="^prod_"))
    app.add_handler(CallbackQueryHandler(handle_coating_selection, pattern="^coating_"))
    app.add_handler(CallbackQueryHandler(select_coating, pattern="^select_coating_"))
    app.add_handler(CallbackQueryHandler(enter_ral_color, pattern="^enter_ral_"))
    app.add_handler(CallbackQueryHandler(confirm_add_to_cart, pattern="^confirm_add_"))
    app.add_handler(CallbackQueryHandler(form_order, pattern="^form_order$"))
    app.add_handler(CallbackQueryHandler(ask_question, pattern="^ask_question$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен в режиме webhook")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://metalfencingbot.onrender.com/{TOKEN}" 
    )

if __name__ == "__main__":
    main()
