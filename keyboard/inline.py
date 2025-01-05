from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_functions_keyboard():
    """Функция для создания клавиатуры."""
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text="🏢 О нас", callback_data="about_us"))
    keyboard.add(InlineKeyboardButton(text="🤖 О боте", callback_data="about_bot"))
    keyboard.add(InlineKeyboardButton(text="🔢 Узнать о калькуляторе", callback_data="calculator_functions"))
    keyboard.add(InlineKeyboardButton(text="🌐 Сайты поставщиков", callback_data="suppliers2_sites"))
    keyboard.add(InlineKeyboardButton(text="🔍 Найти поставщика по товару", callback_data="find_supplier"))
    keyboard.add(InlineKeyboardButton(text="📍 Найти поставщика по городу", callback_data="find_supplier_by_city"))
    keyboard.add(InlineKeyboardButton(text="📅 Связаться с нами", callback_data="contact_us"))

    return keyboard.adjust(2, 1, 1, 1, 1).as_markup()


def return_menu_functions_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start"))
    return keyboard.adjust(1, ).as_markup()


def return2_menu_functions_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start_"))
    return keyboard.adjust(1, ).as_markup()


def get_cancel_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel"))
    return keyboard.adjust(1).as_markup()


def start_admin_inline_keyboard():
    keyboard = InlineKeyboardBuilder()

    # Добавляем кнопки
    keyboard.add(
        InlineKeyboardButton(text="➕ Добавить поставщика", callback_data="add_supplier"),
        InlineKeyboardButton(text="📦 Все поставщики", callback_data="all_suppliers"),
        InlineKeyboardButton(text="📊 Статистика бота", callback_data="bot_statistics"),
        InlineKeyboardButton(text="➕ Добавить администратора", callback_data="add_admin"),
        InlineKeyboardButton(text="👥 Список администраторов", callback_data="list_admins")  # Кнопка для списка админов
    )
    return keyboard.adjust(2, 1).as_markup()


def return_admin_panel_functions_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start_admin"))
    return keyboard.adjust(1, ).as_markup()
