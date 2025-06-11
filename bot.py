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

# ========== ДАННЫЕ О ТОВАРАХ ==========
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
            "description": "Снегозадержатель СТС «ПРОФ» для кровель из профнастила и сэндвич-панелей.",
            "specs": ["Кровля из сэндвич панели", "Кровля из профнастила высокой волны"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 3475, "Цинк+краска": 3735},
            "photo": "СТС «ПРОФ».jpg"
        },
        {
            "id": "1_2",
            "name": "СТС «Усиленный универсальный»",
            "description": "Усиленный универсальный снегозадержатель для различных типов кровли.",
            "specs": ["Универсальное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 4200, "Цинк+краска": 4500},
            "photo": "СТС «Усиленный универсальный».jpg"
        },
        {
            "id": "1_3",
            "name": "СТС «Усиленный фальц»",
            "description": "Усиленный снегозадержатель для фальцевых кровель.",
            "specs": ["Фальцевая кровля"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 4300, "Цинк+краска": 4600},
            "photo": "СТС «Усиленный фальц».jpg"
        },
        {
            "id": "1_4",
            "name": "СТС «Универсальный»",
            "description": "Универсальный снегозадержатель для большинства типов кровель.",
            "specs": ["Универсальное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 3800, "Цинк+краска": 4100},
            "photo": "СТС «Универсальный».jpg"
        },
        {
            "id": "1_5",
            "name": "СТС «Фальц»",
            "description": "Снегозадержатель для фальцевых кровель.",
            "specs": ["Фальцевая кровля"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 3900, "Цинк+краска": 4200},
            "photo": "СТС «Фальц».jpg"
        },
        {
            "id": "1_6",
            "name": "СТС «Решетчатый универсальный»",
            "description": "Решетчатый универсальный снегозадержатель.",
            "specs": ["Универсальное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 4000, "Цинк+краска": 4300},
            "photo": "СТС «Решетчатый универсальный».jpg"
        },
        {
            "id": "1_7",
            "name": "СТС «Решётчатый фальц»",
            "description": "Решетчатый снегозадержатель для фальцевых кровель.",
            "specs": ["Фальцевая кровля"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 4100, "Цинк+краска": 4400},
            "photo": "СТС «Решётчатый фальц».jpg"
        },
        {
            "id": "1_8",
            "name": "СТС «Фигурный универсальный»",
            "description": "Фигурный универсальный снегозадержатель.",
            "specs": ["Универсальное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 4200, "Цинк+краска": 4500},
            "photo": "СТС «Фигурный универсальный».jpg"
        },
        {
            "id": "1_9",
            "name": "СТС «Фигурный фальц»",
            "description": "Фигурный снегозадержатель для фальцевых кровель.",
            "specs": ["Фальцевая кровля"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 4300, "Цинк+краска": 4600},
            "photo": "СТС «Фигурный фальц».jpg"
        }
    ],
    "2": [
        {
            "id": "2_1",
            "name": "СТС «Для ПВХ кровель»",
            "description": "Кровельное ограждение для ПВХ кровель.",
            "specs": ["ПВХ кровля"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 5200, "Цинк+краска": 5600},
            "photo": "СТС «Для ПВХ кровель».jpg"
        },
        {
            "id": "2_2",
            "name": "Кровельное ограждение СТС «ПРОФ»",
            "description": "Кровельное ограждение для профнастила.",
            "specs": ["Профнастил"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 5300, "Цинк+краска": 5700},
            "photo": "Кровельное ограждение СТС «ПРОФ».jpg"
        },
        {
            "id": "2_3",
            "name": "Кровельное ограждение комбинированное СТС «ПРОФ»",
            "description": "Комбинированное кровельное ограждение.",
            "specs": ["Комбинированное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 5400, "Цинк+краска": 5800},
            "photo": "Кровельное ограждение комбинированное СТС «ПРОФ».jpg"
        },
        {
            "id": "2_4",
            "name": "Кровельное ограждение СТС «Универсальное»",
            "description": "Универсальное кровельное ограждение.",
            "specs": ["Универсальное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 5500, "Цинк+краска": 5900},
            "photo": "Кровельное ограждение СТС «Универсальное».jpg"
        },
        {
            "id": "2_5",
            "name": "Кровельное ограждение СТС «Фальц»",
            "description": "Кровельное ограждение для фальцевых кровель.",
            "specs": ["Фальцевая кровля"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 5600, "Цинк+краска": 6000},
            "photo": "Кровельное ограждение СТС «Фальц».jpg"
        },
        {
            "id": "2_6",
            "name": "Кровельное ограждение комбинированное СТС «Универсальное» 4 опоры",
            "description": "Комбинированное ограждение с 4 опорами.",
            "specs": ["4 опоры"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 5700, "Цинк+краска": 6100},
            "photo": "Кровельное ограждение комбинированное СТС «Универсальное» 4 опоры.jpg"
        },
        {
            "id": "2_7",
            "name": "Кровельное ограждение комбинированное СТС «Фальц» 4 опоры",
            "description": "Комбинированное ограждение для фальца с 4 опорами.",
            "specs": ["Фальцевая кровля", "4 опоры"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 5800, "Цинк+краска": 6200},
            "photo": "Кровельное ограждение комбинированное СТС «Фальц» 4 опоры.jpg"
        },
        {
            "id": "2_8",
            "name": "Кровельное ограждение комбинированное СТС «Универсальное» 3 опоры",
            "description": "Комбинированное ограждение с 3 опорами.",
            "specs": ["3 опоры"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 5900, "Цинк+краска": 6300},
            "photo": "Кровельное ограждение комбинированное СТС «Универсальное» 3 опоры.jpg"
        },
        {
            "id": "2_9",
            "name": "Кровельное ограждение комбинированное СТС «Фальц» 3 опоры",
            "description": "Комбинированное ограждение для фальца с 3 опорами.",
            "specs": ["Фальцевая кровля", "3 опоры"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 6000, "Цинк+краска": 6400},
            "photo": "Кровельное ограждение комбинированное СТС «Фальц» 3 опоры.jpg"
        },
        {
            "id": "2_10",
            "name": "Кровельное ограждение парапетное СТС «В»",
            "description": "Парапетное ограждение типа В.",
            "specs": ["Парапетное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 6100, "Цинк+краска": 6500},
            "photo": "Кровельное ограждение парапетное СТС «В».jpg"
        },
        {
            "id": "2_11",
            "name": "Кровельное ограждение парапетное СТС «Г»",
            "description": "Парапетное ограждение типа Г.",
            "specs": ["Парапетное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 6200, "Цинк+краска": 6600},
            "photo": "Кровельное ограждение парапетное СТС «Г».jpg"
        },
        {
            "id": "2_12",
            "name": "Кровельное ограждение СТС «ПРОФ» для плоских кровель 3 опоры",
            "description": "Ограждение для плоских кровель с 3 опорами.",
            "specs": ["Плоская кровля", "3 опоры"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 6300, "Цинк+краска": 6700},
            "photo": "Кровельное ограждение СТС «ПРОФ» для плоских кровель 3 опоры.jpg"
        }
    ],
    "3": [
        {
            "id": "3_1",
            "name": "Площадка выхода на кровлю ЛП/СТС/800",
            "description": "Площадка выхода на кровлю.",
            "specs": ["Стандартная"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 7200, "Цинк+краска": 7600},
            "photo": "Площадка выхода на кровлю ЛП/СТС/800.jpg"
        },
        {
            "id": "3_2",
            "name": "Лестница пожарная ЛП/СТС/800 (без площадки)",
            "description": "Пожарная лестница без площадки.",
            "specs": ["Стандартная"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 7300, "Цинк+краска": 7700},
            "photo": "Лестница пожарная ЛП/СТС/800 (без площадки).jpg"
        }
    ],
    "4": [
        {
            "id": "4_1",
            "name": "Лестница стеновая СТС",
            "description": "Стеновая лестница.",
            "specs": ["Стандартная"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 8200, "Цинк+краска": 8600},
            "photo": "Лестница стеновая СТС.jpg"
        },
        {
            "id": "4_2",
            "name": "Лестница кровельная СТС «Универсальный»",
            "description": "Универсальная кровельная лестница.",
            "specs": ["Универсальное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 8300, "Цинк+краска": 8700},
            "photo": "Лестница кровельная СТС «Универсальный».jpg"
        },
        {
            "id": "4_3",
            "name": "Лестница кровельная СТС «ПРОФ»",
            "description": "Кровельная лестница для профнастила.",
            "specs": ["Профнастил"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 8400, "Цинк+краска": 8800},
            "photo": "Лестница кровельная СТС «ПРОФ».jpg"
        },
        {
            "id": "4_4",
            "name": "Лестница кровельная СТС «Фальц»",
            "description": "Кровельная лестница для фальцевых кровель.",
            "specs": ["Фальцевая кровля"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 8500, "Цинк+краска": 8900},
            "photo": "Лестница кровельная СТС «Фальц».jpg"
        }
    ],
    "5": [
        {
            "id": "5_1",
            "name": "Мостик кровельный СТС «ПРОФ»",
            "description": "Кровельный мостик для профнастила.",
            "specs": ["Профнастил"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 9200, "Цинк+краска": 9600},
            "photo": "Мостик кровельный СТС «ПРОФ».jpg"
        },
        {
            "id": "5_2",
            "name": "Мостик кровельный СТС «Универсальный»",
            "description": "Универсальный кровельный мостик.",
            "specs": ["Универсальное крепление"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 9300, "Цинк+краска": 9700},
            "photo": "Мостик кровельный СТС «Универсальный».jpg"
        },
        {
            "id": "5_3",
            "name": "Мостик кровельный СТС «Фальц»",
            "description": "Кровельный мостик для фальцевых кровель.",
            "specs": ["Фальцевая кровля"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 9400, "Цинк+краска": 9800},
            "photo": "Мостик кровельный СТС «Фальц».jpg"
        },
        {
            "id": "5_4",
            "name": "Ограждение к кровельному мостику СТС",
            "description": "Ограждение для кровельного мостика.",
            "specs": ["Стандартное"],
            "coating": ["Цинк", "Цинк+краска"],
            "price": {"Цинк": 9500, "Цинк+краска": 9900},
            "photo": "Ограждение к кровельному мостику СТС.jpg"
        }
    ]
}

# Глобальные переменные для хранения состояния
user_carts = {}  # Корзины пользователей
user_states = {}  # Текущие состояния пользователей
user_selections = {}  # Выборы пользователей

# ========== ФОРМАТИРОВАНИЕ СООБЩЕНИЙ ==========
def format_product_message(product, selected_options=None):
    message = f"📦 <b>{product['name']}</b>\n\n"
    message += f"📝 <i>{product['description']}</i>\n\n"
    
    if selected_options:
        for option, value in selected_options.items():
            if option == "Цвет, RAL Classic" and value == "Не выбрано":
                continue
            message += f"🔹 {option}: {value}\n"
    
    if 'price' in product:
        if isinstance(product['price'], dict):
            if selected_options and 'Защитное покрытие' in selected_options:
                coating = selected_options['Защитное покрытие']
                price = product['price'].get(coating, 0)
                message += f"\n💰 Цена: {price} руб./шт\n"
            else:
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
    user_selections[user_id] = {}  # Сброс выбора пользователя
    
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
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)

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
    user_id = str(query.from_user.id)
    user_states[user_id] = "CATALOG"
    
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
    user_id = str(query.from_user.id)
    user_states[user_id] = f"CATEGORY_{category_id}"
    
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

async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[1]
    user_id = str(query.from_user.id)
    user_states[user_id] = f"PRODUCT_{product_id}"
    
    # Находим продукт по ID
    product = None
    for cat_id, cat_products in products.items():
        for p in cat_products:
            if p['id'] == product_id:
                product = p
                break
        if product:
            break
    
    if not product:
        await query.edit_message_text("⚠️ Товар не найден.")
        return
    
    # Сохраняем текущий продукт для пользователя
    user_selections[user_id] = {
        "product_id": product_id,
        "product": product,
        "selected_options": {}
    }
    
    # Создаем кнопки для выбора спецификации
    keyboard = []
    if 'specs' in product and product['specs'] and product['specs'][0] != "Нет вариантов":
        keyboard.append([InlineKeyboardButton("📌 Выбрать спецификацию", callback_data=f"spec_{product_id}")])
    
    # Добавляем кнопки для выбора покрытия, если оно есть
    if 'coating' in product and product['coating']:
        keyboard.append([InlineKeyboardButton("🛡 Выбрать покрытие", callback_data=f"select_coating_{product_id}_0")])
    
    keyboard.append([InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"add_to_cart_{product_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"cat_{product_id.split('_')[0]}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с информацией о товаре
    await query.edit_message_text(
        format_product_message(product),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def select_specification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[1]
    user_id = str(query.from_user.id)
    
    product = None
    for cat in products.values():
        for p in cat:
            if p['id'] == product_id:
                product = p
                break
        if product:
            break
    
    if not product:
        await query.edit_message_text("⚠️ Товар не найден.")
        return
    
    keyboard = [
        [InlineKeyboardButton(spec, callback_data=f"select_spec_{product_id}_{i}")]
        for i, spec in enumerate(product['specs'])
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"prod_{product_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "📌 Выберите спецификацию:",
        reply_markup=reply_markup
    )

async def handle_spec_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, product_id, spec_index = query.data.split("_")[1:]
    spec_index = int(spec_index)
    user_id = str(query.from_user.id)
    
    product = None
    for cat in products.values():
        for p in cat:
            if p['id'] == product_id:
                product = p
                break
        if product:
            break
    
    if not product:
        await query.edit_message_text("⚠️ Товар не найден.")
        return
    
    # Сохраняем выбранную спецификацию
    user_selections[user_id]["selected_options"]["Спецификация"] = product['specs'][spec_index]
    
    # Переходим к выбору покрытия
    keyboard = [
        [InlineKeyboardButton(coating, callback_data=f"select_coating_{product_id}_{i}")]
        for i, coating in enumerate(product['coating'])
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"spec_{product_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🛡 Выберите защитное покрытие:",
        reply_markup=reply_markup
    )

async def handle_coating_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, product_id, coating_index = query.data.split("_")[1:]
    coating_index = int(coating_index)
    user_id = str(query.from_user.id)
    
    product = None
    for cat in products.values():
        for p in cat:
            if p['id'] == product_id:
                product = p
                break
        if product:
            break
    
    if not product:
        await query.edit_message_text("⚠️ Товар не найден.")
        return
    
    # Сохраняем выбранное покрытие
    selected_coating = product['coating'][coating_index]
    user_selections[user_id]["selected_options"]["Защитное покрытие"] = selected_coating
    
    # Если выбрано "Цинк+краска", предлагаем выбрать цвет
    if selected_coating == "Цинк+краска":
        keyboard = [
            [InlineKeyboardButton("Ввести цвет RAL", callback_data=f"enter_ral_{product_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"select_coating_{product_id}_0")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎨 Вы выбрали Цинк+краска. Пожалуйста, укажите цвет по каталогу RAL Classic (четырехзначное число):",
            reply_markup=reply_markup
        )
    else:
        # Переходим к выбору количества
        await select_quantity(update, context, product_id)

async def enter_ral_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[2]
    user_id = str(query.from_user.id)
    user_states[user_id] = f"AWAITING_RAL_{product_id}"
    
    await query.edit_message_text(
        "✏️ Введите четырехзначный код цвета RAL (например, 3005):"
    )

async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id=None):
    if not product_id:
        query = update.callback_query
        await query.answer()
        product_id = query.data.split("_")[2]
    
    user_id = str(update.effective_user.id)
    user_states[user_id] = f"AWAITING_QUANTITY_{product_id}"
    
    product = None
    for cat in products.values():
        for p in cat:
            if p['id'] == product_id:
                product = p
                break
        if product:
            break
    
    if not product:
        await update.message.reply_text("⚠️ Товар не найден.")
        return
    
    # Если это вызов из handle_coating_selection, используем query
    if hasattr(update, 'callback_query'):
        query = update.callback_query
        await query.edit_message_text(
            "🔢 Введите количество товара (в штуках):"
        )
    else:
        # Если это вызов после ввода RAL цвета
        await update.message.reply_text(
            "🔢 Введите количество товара (в штуках):"
        )

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
        await update.message.reply_text("⚠️ Пожалуйста, введите корректное количество (целое число больше 0):")
        return
    
    # Сохраняем количество
    user_selections[user_id]["selected_options"]["Количество"] = quantity
    
    # Рассчитываем итоговую цену
    product = user_selections[user_id]["product"]
    selected_options = user_selections[user_id]["selected_options"]
    
    if 'Защитное покрытие' in selected_options:
        coating = selected_options['Защитное покрытие']
        price_per_item = product['price'].get(coating, 0)
        total_price = price_per_item * quantity
        selected_options["Итоговая цена"] = total_price
    
    # Показываем итоговую информацию
    keyboard = [
        [InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"confirm_add_{product_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"prod_{product_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Вы выбрали:\n\n{format_product_message(product, user_selections[user_id]['selected_options'])}\n\n"
        f"🔄 Итоговая сумма: {selected_options.get('Итоговая цена', 0)} руб.",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def confirm_add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = query.data.split("_")[2]
    user_id = str(query.from_user.id)
    
    if user_id not in user_selections or user_selections[user_id]["product_id"] != product_id:
        await query.edit_message_text("⚠️ Ошибка добавления в корзину. Пожалуйста, начните выбор заново.")
        return
    
    # Добавляем товар в корзину
    cart_item = {
        "product": user_selections[user_id]["product"],
        "selected_options": user_selections[user_id]["selected_options"].copy()
    }
    
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    user_carts[user_id].append(cart_item)
    
    # Показываем сообщение об успешном добавлении
    keyboard = [
        [InlineKeyboardButton("📦 Перейти в корзину", callback_data="view_cart")],
        [InlineKeyboardButton("🛒 Продолжить покупки", callback_data="catalog")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "✅ Товар успешно добавлен в корзину!",
        reply_markup=reply_markup
    )

# ========== ОБРАБОТЧИКИ СООБЩЕНИЙ ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    current_state = user_states.get(user_id, "MAIN_MENU")
    
    if current_state.startswith("AWAITING_RAL_"):
        product_id = current_state.split("_")[2]
        ral_color = update.message.text.strip()
        
        # Простая валидация RAL цвета (4 цифры)
        if not (ral_color.isdigit() and len(ral_color) == 4):
            await update.message.reply_text("⚠️ Пожалуйста, введите корректный код RAL (четыре цифры):")
            return
        
        user_selections[user_id]["selected_options"]["Цвет, RAL Classic"] = f"RAL {ral_color}"
        await select_quantity(update, context, product_id)
    
    elif current_state.startswith("AWAITING_QUANTITY_"):
        await handle_quantity_input(update, context)
    
    elif current_state == "AWAITING_QUESTION":
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
    app.add_handler(CallbackQueryHandler(show_product, pattern="^prod_"))
    app.add_handler(CallbackQueryHandler(select_specification, pattern="^spec_"))
    app.add_handler(CallbackQueryHandler(handle_spec_selection, pattern="^select_spec_"))
    app.add_handler(CallbackQueryHandler(handle_coating_selection, pattern="^select_coating_"))
    app.add_handler(CallbackQueryHandler(enter_ral_color, pattern="^enter_ral_"))
    app.add_handler(CallbackQueryHandler(confirm_add_to_cart, pattern="^confirm_add_"))
    
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
