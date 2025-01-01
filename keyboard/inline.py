from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_functions_keyboard():
    """Функция для создания клавиатуры."""
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text="🏢 О нас", callback_data="about_us"))
    keyboard.add(InlineKeyboardButton(text="🤖 О боте", callback_data="about_bot"))
    keyboard.add(InlineKeyboardButton(text="🔢 Узнать о калькуляторе", callback_data="calculator_functions"))
    keyboard.add(InlineKeyboardButton(text="🌐 Сайты поставщиков", callback_data="suppliers_sites"))
    keyboard.add(InlineKeyboardButton(text="📜 История запросов", callback_data="history"))
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