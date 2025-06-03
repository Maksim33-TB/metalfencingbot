from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os

# Получаем порт из переменной окружения или используем 8000 по умолчанию
PORT = int(os.environ.get('PORT', 8000))

# ========== ТОКЕН ==========
TOKEN = '8159127478:AAHwjKl3zeZ3LZ4RgJgZ9X4Y1WOOKQFyZww'

# ========== АДМИНЫ ДЛЯ ЗАЯВОК ==========
MANAGER_CHAT_ID = "@MaksimS1989"  # Заменить на настоящий ID
ADMIN_CHAT_ID = "777000"     # Заменить на настоящий ID

# ========== ДАННЫЕ О ТОВАРАХ ==========

products_data = {
    "snow_retainer": [
        {
            "id": "1",
            "name": "СТС «ПРОФ»",
            "description": "Снегозадержатель СТС «ПРОФ» длиной 3000 мм предназначен для кровель из профнастила выше НС40 и сендвич-панелей любого производителя.",
            "specifications": ["Кровля из сэндвич панели", "Кровля из профнастила высокой волны"],
            "coating_options": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": "3475 руб./шт", "Цинк+краска": "3735 руб./шт"},
            "image": "СТС_«ПРОФ».jpg"
        },
        {
            "id": "2",
            "name": "СТС «Универсальный усиленный»",
            "description": "Снегозадержатель СТС «Универсальный усиленный» длиной 3000 мм подходит для всех видов кровельных материалов.",
            "specifications": ["Нет вариантов"],
            "coating_options": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": "2805 руб./шт", "Цинк+краска": "3100 руб./шт"},
            "image": "СТС_«Усиленный_универсальный».jpg"
        },
        {
            "id": "3",
            "name": "СТС «Универсальный»",
            "description": "Снегозадержатель СТС «Универсальный» длиной 3000 мм подходит для всех видов кровельных материалов.",
            "specifications": ["Нет вариантов"],
            "coating_options": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": "2350 руб./шт", "Цинк+краска": "2640 руб./шт"},
            "image": "СТС_«Универсальный».jpg"
        }
    ],
    "roof_railing": [
        {
            "id": "4",
            "name": "СТС «Для ПВХ кровель»",
            "description": "Кровельное ограждение СТС «Для ПВХ кровель» длиной 3000 мм, высотой 600/800/1200 мм.",
            "heights": ["600 мм", "800 мм", "1200 мм"],
            "cross_tubes": {"600 мм": ["2"], "800 мм": ["2", "3"], "1200 мм": ["2", "3"]},
            "coating_options": ["Цинк", "Цинк+краска"],
            "price": {
                "600 мм": {"Цинк": "7650 руб./шт", "Цинк+краска": "8100 руб./шт"},
                "800 мм": {"Цинк": "7830 руб./шт", "Цинк+краска": "8290 руб./шт"},
                "1200 мм": {"Цинк": "9120 руб./шт", "Цинк+краска": "9540 руб./шт"}
            },
            "image": "Кровельное_ограждение_СТС_«Для_ПВХ_кровель».jpg"
        }
    ],
    # Можно добавить остальные категории по аналогии
}

# ========== ХРАНИЛИЩЕ ==========
user_state = {}  # {user_id: {"stage": "...", "product": {}, "quantity": "", ...}}
user_cart = {}   # {user_id: [{"product": ..., "quantity": ..., "total_price": ...}, ...]}

# ========== ГЛАВНОЕ МЕНЮ ==========
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🏢 О компании", callback_data="company")],
        [InlineKeyboardButton("🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== КАТАЛОГ МЕНЮ ==========
def catalog_menu():
    buttons = [
        [InlineKeyboardButton("❄️ Снегозадержатели", callback_data="snow_retainer")],
        [InlineKeyboardButton("🪜 Кровельные ограждения", callback_data="roof_railing")],
        [InlineKeyboardButton("🔥 Пожарные лестницы", callback_data="fire_ladder")],
        [InlineKeyboardButton("🪜 Лестницы", callback_data="ladder")],
        [InlineKeyboardButton("🌉 Переходные мостики", callback_data="bridge")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(buttons)

# ========== СООБЩЕНИЕ О ТОВАРЕ ==========
def product_message(product):
    message = f"📦 <b>{product['name']}</b>\n\n📝 <i>{product['description']}</i>\n\n"

    if 'specifications' in product and product['specifications'][0] != "Нет вариантов":
        message += f"🧱 Спецификация: {'/'.join(product['specifications'])}\n"

    if 'heights' in product and product['heights'] and product['heights'][0] != "Нет вариантов":
        message += f"📐 Высота: {'/'.join(product['heights'])}\n"

    if 'cross_tubes' in product and any(product['cross_tubes'].values()):
        message += f"🧱 Кол-во поперечных труб: зависит от высоты\n"

    message += f"🎨 Защитное покрытие: {'/'.join(product['coating_options'])}\n"
    message += f"💰 Цена: {product['price']}"
    return message

# ========== КОМАНДА /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = {"stage": "main_menu"}
    user_cart[user_id] = []

    await update.message.reply_text(
        "👋 Вас приветствует официальный бот продаж продукции ООО «СТС»! Мы предлагаем элементы безопасности на ВСЕ типы кровель, цены завода изготовителя, отгрузка от 1 дня.\n\n"
        "🛒 Воспользуйтесь нашим онлайн-решением для удобного формирования заявок на покупку продукции!",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# ========== ОБРАБОТЧИК КНОПОК ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # Управление состоянием пользователя
    state = user_state.get(user_id, {"stage": "main_menu"})
    current_stage = state["stage"]

    # Обработка главного меню
    if data == "main_menu":
        user_state[user_id]["stage"] = "main_menu"
        await query.edit_message_text(
            "🏠 Главное меню",
            reply_markup=main_menu()
        )

    elif data == "company":
        company_text = (
            "🏛 <b>О компании</b>\n\n"
            "Компания ООО «СТС» работает в области производства элементов безопасности кровли с 2014 года.\n"
            "Мы применяем высокоточные станки, а на нашем производстве задействованы специалисты с опытом от 5 лет.\n"
            "Мы осуществляем бесплатную доставку до терминала транспортной компании в вашем городе.\n"
            "🔗 Официальный сайт: <a href='https://эбк-стс.рф'>эбк-стс.рф</a>" 
        )
        await query.edit_message_text(company_text, parse_mode="HTML")
        await query.message.reply_text("⬅️ Вернуться в главное меню", reply_markup=main_menu())

    elif data == "contacts":
        contacts_text = (
            "📬 <b>Контакты</b>\n\n"
            "📧 Наш e-mail: ctcnet@yandex.ru\n"
            "📞 Задать вопрос можно по этим контактам:\n"
            "+7 910 090 4945 — менеджер\n"
            "+7 903 258 73 32 — администратор"
        )
        keyboard = [[InlineKeyboardButton("💬 Задать вопрос", callback_data="ask_question")]]
        await query.edit_message_text(contacts_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        await query.message.reply_text("⬅️ Вернуться в главное меню", reply_markup=main_menu())

    elif data == "ask_question":
        user_state[user_id]["stage"] = "awaiting_question"
        await query.edit_message_text("✍️ Пожалуйста, напишите ваш вопрос:")

    elif data == "catalog":
        user_state[user_id]["stage"] = "catalog"
        buttons = []
        for cat in products_data.keys():
            buttons.append([InlineKeyboardButton(cat.capitalize(), callback_data=f"catalog_{cat}")])
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
        await query.edit_message_text("📂 Выберите категорию:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("catalog_"):
        category = data.split("_")[1]
        user_state[user_id]["stage"] = f"select_{category}"
        buttons = []
        for idx, item in enumerate(products_data[category], start=1):
            buttons.append([InlineKeyboardButton(item['name'], callback_data=f"{category}_{idx}")]
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog")])
        await query.edit_message_text("🛠 Выберите модель:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("snow_retainer_"):
        model_id = data.split("_")[2]
        product = next((p for p in products_data["snow_retainer"] if p["id"] == model_id), None)
        if product:
            user_state[user_id]["stage"] = "select_coating_snow"
            user_state[user_id]["product"] = product
            coating_buttons = [[InlineKeyboardButton(coat, callback_data=f"coating_{coat}_snow")]
                               for coat in product["coating_options"]]
            coating_buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"catalog_snow_retainer")])
            await query.edit_message_text("🎨 Выберите защитное покрытие:",
                                        reply_markup=InlineKeyboardMarkup(coating_buttons))

    elif data.startswith("roof_railing_"):
        model_id = data.split("_")[2]
        product = next((p for p in products_data["roof_railing"] if p["id"] == model_id), None)
        if product:
            user_state[user_id]["stage"] = "select_height_roof"
            user_state[user_id]["product"] = product
            height_buttons = [[InlineKeyboardButton(h, callback_data=f"height_{h}_roof")] for h in product["heights"]]
            height_buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"catalog_roof_railing")])
            await query.edit_message_text("📐 Выберите высоту:", reply_markup=InlineKeyboardMarkup(height_buttons))

    elif data.startswith("height_"):
        height = data.split("_")[1]
        type_ = data.split("_")[2]
        user_state[user_id]["height"] = height
        user_state[user_id]["stage"] = "select_cross_tubes_roof"
        cross_tubes = user_state[user_id]["product"]["cross_tubes"].get(height, [])
        if len(cross_tubes) <= 1:
            user_state[user_id]["cross_tubes"] = cross_tubes[0] if cross_tubes else "Нет"
            user_state[user_id]["stage"] = "select_coating_roof"
            coating_buttons = [[InlineKeyboardButton(coat, callback_data=f"coating_{coat}_roof")] 
                               for coat in user_state[user_id]["product"]["coating_options"]]
            coating_buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog_roof_railing")])
            await query.edit_message_text("🎨 Выберите защитное покрытие:", reply_markup=InlineKeyboardMarkup(coating_buttons))
        else:
            tube_buttons = [[InlineKeyboardButton(t, callback_data=f"tubes_{t}_roof")] for t in cross_tubes]
            tube_buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog_roof_railing")]
            await query.edit_message_text("🔧 Выберите количество поперечных труб:", reply_markup=InlineKeyboardMarkup(tube_buttons))

    elif data.startswith("tubes_"):
        tubes = data.split("_")[1]
        user_state[user_id]["cross_tubes"] = tubes
        user_state[user_id]["stage"] = "select_coating_roof"
        coating_buttons = [[InlineKeyboardButton(coat, callback_data=f"coating_{coat}_roof")] 
                           for coat in user_state[user_id]["product"]["coating_options"]]
        coating_buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog_roof_railing")])
        await query.edit_message_text("🎨 Выберите защитное покрытие:", reply_markup=InlineKeyboardMarkup(coating_buttons))

    elif data.startswith("coating_"):
        coating = data.split("_")[1]
        category = data.split("_")[2]
        user_state[user_id]["coating"] = coating

        if coating == "Цинк+краска":
            ral_buttons = [[InlineKeyboardButton(f"RAL {i}", callback_data=f"ral_{i}_{category}")] for i in range(1000, 9999)]
            ral_buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"catalog_{category}")])
            await query.edit_message_text("🎨 Выберите цвет RAL:", reply_markup=InlineKeyboardMarkup(ral_buttons))
        else:
            user_state[user_id]["stage"] = "enter_quantity"
            await query.edit_message_text("🔢 Введите количество штук:")

    elif data.startswith("ral_"):
        ral_code = data.split("_")[1]
        category = data.split("_")[3]
        user_state[user_id]["ral"] = ral_code
        user_state[user_id]["stage"] = "enter_quantity"
        await query.edit_message_text("🔢 Введите количество штук:")

    elif data == "add_to_cart":
        # Добавление в корзину
        product = user_state[user_id].get("product")
        quantity = user_state[user_id].get("quantity", "1")
        price = product["price"][user_state[user_id]["coating"]]
        total_price = int(price.split()[0]) * int(quantity)

        user_cart[user_id].append({
            "product": product,
            "quantity": quantity,
            "total_price": f"{total_price} руб."
        })

        user_state[user_id]["stage"] = "in_cart"
        cart_buttons = [
            [InlineKeyboardButton("🛒 Продолжить покупку", callback_data="continue_shopping")],
            [InlineKeyboardButton("📥 Сформировать заявку", callback_data="form_order")]
        ]
        cart_text = "🛒 Вы можете продолжить покупку или оформить заказ сейчас:\n\n"
        for idx, item in enumerate(user_cart[user_id]):
            cart_text += f"{idx + 1}. {item['product']['name']} x{item['quantity']} - {item['total_price']}\n"

        await query.edit_message_text(cart_text, reply_markup=InlineKeyboardMarkup(cart_buttons))

    elif data == "continue_shopping":
        user_state[user_id]["stage"] = "catalog"
        await query.edit_message_text("🛠 Выберите товар:", reply_markup=catalog_menu())

    elif data == "form_order":
        user_state[user_id]["stage"] = "order_form_name"
        await query.edit_message_text("👤 Введите ваше имя:")

    elif data == "back_to_catalog":
        user_state[user_id]["stage"] = "catalog"
        await query.edit_message_text("🛠 Выберите товар:", reply_markup=catalog_menu())

    elif data == "back_to_main":
        await query.edit_message_text("🏠 Главное меню", reply_markup=main_menu())
        user_state[user_id]["stage"] = "main_menu"

# ========== ОБРАБОТКА ТЕКСТА ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_state.get(user_id, {}).get("stage") == "awaiting_question":
        phone = "Не указан"
        email = "Не указан"
        message = (
            f"❗ Новый вопрос от пользователя:\n\n"
            f"📝 Текст: {text}\n"
            f"📞 Телефон: {phone}\n"
            f"📧 Email: {email}"
        )
        await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=message)
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
        await update.message.reply_text("✅ Ваш вопрос отправлен!")

    elif user_state.get(user_id, {}).get("stage") == "order_form_name":
        user_state[user_id]["name"] = text
        user_state[user_id]["stage"] = "order_form_phone"
        await update.message.reply_text("📞 Введите ваш телефон:")

    elif user_state.get(user_id, {}).get("stage") == "order_form_phone":
        user_state[user_id]["phone"] = text
        user_state[user_id]["stage"] = "order_form_email"
        await update.message.reply_text("📧 Введите ваш email (можно пропустить):")

    elif user_state.get(user_id, {}).get("stage") == "order_form_email":
        user_state[user_id]["email"] = text or "Не указан"
        await send_order_summary(update, context)

    elif user_state.get(user_id, {}).get("stage") == "enter_quantity":
        user_state[user_id]["quantity"] = text
        product = user_state[user_id]["product"]
        coating = user_state[user_id]["coating"]
        price = product["price"][coating]
        total_price = int(price.split()[0]) * int(text)

        cart_buttons = [
            [InlineKeyboardButton("➕ Добавить в корзину", callback_data="add_to_cart")],
            [InlineKeyboardButton("🔄 Изменить количество", callback_data="change_quantity")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_catalog")]
        ]

        summary = (
            f"📦 <b>{product['name']}</b>\n"
            f"🎨 Покрытие: {coating}\n"
            f"🔢 Количество: {text}\n"
            f"💰 Итого: {total_price} руб."
        )

        await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(cart_buttons))

# ========== ОТПРАВКА СВОДНОЙ ЗАЯВКИ ==========
async def send_order_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    order = user_state[user_id]
    cart = user_cart[user_id]

    summary = (
        "📄 <b>Ваша заявка:</b>\n\n"
        f"👤 Имя: {order.get('name', '')}\n"
        f"📞 Телефон: {order.get('phone', '')}\n"
        f"📧 Email: {order.get('email', '')}\n\n"
        f"📦 Продукция:\n"
    )

    total = 0
    for item in cart:
        summary += f"- {item['product']['name']} x{item['quantity']} — {item['total_price']}\n"
        total += int(item['total_price'].split()[0])

    summary += f"\n💰 Общая сумма: {total} руб."

    await update.callback_query.edit_message_text(summary, parse_mode="HTML")
    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=summary, parse_mode="HTML")
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary, parse_mode="HTML")

    confirmation = (
        "✅ Благодарим за сформированный запрос!\n\n"
        "• После оформления заказа, в течение 60 минут, Вам перезвонит менеджер для согласования всех нюансов и подтверждения заказа.\n"
        "• Режим работы менеджеров: Пн.-Пт.: 9:00—17:00\n"
        "• Далее мы выставляем счет на оплату\n"
        "• После оплаты — заказ отправляется на комплектацию\n"
        "• Отгрузка занимает от 1 дня\n"
        "• Готовый к выдачи заказ можно забрать самостоятельно или воспользоваться услугами ТК (по умолчанию — Деловые Линии)\n"
        "• При доставке ТК номер накладной будет отправлен вам в чат"
    )
    await update.effective_message.reply_text(confirmation, reply_markup=main_menu())

# ========== ЗАПУСК БОТА ==========
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен в режиме webhook")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://metalfencingbot.onrender.com/{TOKEN}" 
    )
