from aiogram import F, types, Router, Bot
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import *
from filter.chat_types import ChatTypeFilter
from keyboard.inline import *

start_functions_private_router = Router()
start_functions_private_router.message.filter(ChatTypeFilter(['private']))

# Приветственное сообщение
welcome_text = (
    "Добро пожаловать в MetalPriceBot! 🎉\n\n"
    "Этот бот поможет вам быстро рассчитать стоимость металлопроката. 💰\n\n"
    "Выберите одну из опций ниже, чтобы начать. 🔽"
)


@start_functions_private_router.message(CommandStart())
async def start_cmd(message: types.Message,session: AsyncSession):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    users = await orm_get_id_bot_user(session)
    if user_id not in users:
        name = f"{message.from_user.first_name}"
        username = f"@{message.from_user.username}" if message.from_user.username else ''
        await orm_add_bot_users(session, user_id=user_id, name=name, username=username)

    await message.answer_photo(
        photo=types.FSInputFile('media/img.png'),
        caption=welcome_text,
        reply_markup= start_functions_keyboard()
    )



@start_functions_private_router.callback_query(F.data == "start")
async def start_main_menu(query: types.CallbackQuery, ):
    """Обработчик callback_query для основного меню"""
    await query.message.edit_caption(
        caption=welcome_text,
        reply_markup=start_functions_keyboard())


@start_functions_private_router.callback_query(F.data == "start_")
async def start_main_menu(query: types.CallbackQuery, ):
    """Обработчик callback_query для основного меню"""
    await query.message.delete()
    await query.message.answer_photo(
        photo=types.FSInputFile('media/img.png'),
        caption=welcome_text,
        reply_markup=start_functions_keyboard()
    )


@start_functions_private_router.callback_query(F.data == "about_us")
async def about_us(query: types.CallbackQuery):
    """Обработчик callback_query для кнопки 'О нас'"""
    await query.message.edit_caption(
        caption="Здесь будет текст о нас. Пожалуйста, предоставьте описание вашей компании или проекта, "
                "которое вы хотите разместить в этом разделе.",
        reply_markup=return_menu_functions_keyboard()
    )


@start_functions_private_router.message(Command("about_us"))
async def about_us_message(query: types.Message):
    """Обработчик для кнопки 'about_us'"""
    await query.reply(
        text="Здесь будет текст о нас. Пожалуйста, предоставьте описание вашей компании или проекта, "
                "которое вы хотите разместить в этом разделе.",
        reply_markup=return2_menu_functions_keyboard()
    )


@start_functions_private_router.callback_query(F.data == "about_bot")
async def about_bot(query: types.CallbackQuery):
    """Обработчик callback_query для кнопки 'О боте'"""
    await query.message.edit_caption(
        caption=(
            "<b>Этот бот поможет вам быстро рассчитать стоимость металлопроката.</b>\n"
            "Просто отправьте запрос с нужными параметрами, и я найду актуальную информацию для вас. "
            "Поддерживаются различные виды металлопроката, и я учитываю все параметры: размер, марка, количество и вес. "
            "Легко и удобно! 🤖💬\n\n"

            "<b>Вот что я могу:</b>\n"
            "• <b>О боте 🤖</b> - Узнайте больше о функционале бота\n"
            "• <b>Функции калькулятора 🔢</b> - Откройте калькулятор для расчета стоимости\n"
            "• <b>Сайты поставщиков 🌐</b> - Перейдите к сайтам поставщиков для получения информации\n"
            "• <b>История запросов 📜</b> - Просмотрите историю ваших запросов"
        ),
        reply_markup=return_menu_functions_keyboard()
    )


@start_functions_private_router.message(Command("about_bot"))
async def about_bot_message(query: types.Message):
    """Обработчик для кнопки 'О боте'"""
    await query.reply(
        text=(
            "<b>Этот бот поможет вам быстро рассчитать стоимость металлопроката.</b>\n"
            "Просто отправьте запрос с нужными параметрами, и я найду актуальную информацию для вас. "
            "Поддерживаются различные виды металлопроката, и я учитываю все параметры: размер, марка, количество и вес. "
            "Легко и удобно! 🤖💬\n\n"

            "<b>Вот что я могу:</b>\n"
            "• <b>О боте 🤖</b> - Узнайте больше о функционале бота\n"
            "• <b>Функции калькулятора 🔢</b> - Откройте калькулятор для расчета стоимости\n"
            "• <b>Сайты поставщиков 🌐</b> - Перейдите к сайтам поставщиков для получения информации\n"
            "• <b>История запросов 📜</b> - Просмотрите историю ваших запросов"
        ),
        reply_markup=return2_menu_functions_keyboard()
    )


@start_functions_private_router.callback_query(F.data == "calculator_functions")
async def calculator_functions(query: types.CallbackQuery):
    """Обработчик callback_query для кнопки 'Функции калькулятора'"""
    await query.message.edit_caption(
        caption=(
            "<b>🔢 Калькулятор стоимости металлопроката</b>\n\n"
            "Этот калькулятор поможет вам быстро рассчитать стоимость металлопроката по различным параметрам, таким как:\n\n"
            "• Марка материала\n"
            "• Размер\n"
            "• Количество\n"
            "• Вес\n\n"
            "Просто напишите запрос в формате: <b>'Арматура А500С - 1200 метров'</b>, и я автоматически рассчитаю стоимость!\n\n"
            "<b>💡 Пример запроса:</b>\n"
            "• 'Арматура А500С - 1200 метров'\n"
            "• 'Лист AISI 304 1250x2500 - 79 штук'\n\n"
            "Я помогу вам получить точную информацию о стоимости металлопроката за считанные секунды! 📊📏"
        ),
        reply_markup=return_menu_functions_keyboard()
    )


@start_functions_private_router.message(Command("calculator_functions"))
async def about_bot_message(query: types.Message):
    """Обработчик для кнопки 'О боте'"""
    await query.reply(
        text=(
             "<b>🔢 Калькулятор стоимости металлопроката</b>\n\n"
            "Этот калькулятор поможет вам быстро рассчитать стоимость металлопроката по различным параметрам, "
             "таким как:\n\n"
            "• Марка материала\n"
            "• Размер\n"
            "• Количество\n"
            "• Вес\n\n"
            "Просто напишите запрос в формате: <b>'Арматура А500С - 1200 метров'</b>, и я автоматически рассчитаю стоимость!\n\n"
            "<b>💡 Пример запроса:</b>\n"
            "• 'Арматура А500С - 1200 метров'\n"
            "• 'Лист AISI 304 1250x2500 - 79 штук'\n\n"
            "Я помогу вам получить точную информацию о стоимости металлопроката за считанные секунды! 📊📏"
        ),
        reply_markup=return2_menu_functions_keyboard()
    )


@start_functions_private_router.callback_query(F.data == "suppliers2_sites")
async def suppliers_sites(query: types.CallbackQuery,session: AsyncSession):
    """Обработчик callback_query для кнопки 'Сайты поставщиков'"""
    suppliers = await orm_get_suppliers(session)
    builder = InlineKeyboardBuilder()
    for i in suppliers:
        if i.site_url.startswith("https://"):
            builder.add(InlineKeyboardButton(text=i.title,url=i.site_url))
    builder.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start"))
    await query.message.edit_caption(
        caption="Вот список сайтов поставщиков: 🌍",
        reply_markup=builder.adjust(1).as_markup()
    )


@start_functions_private_router.callback_query(F.data == "contact_us")
async def contact_us(query: types.CallbackQuery):
    """Обработчик callback_query для кнопки 'Связаться с нами'"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="📧 Email", url="https://t.me/duishobaevislam01"),
        InlineKeyboardButton(text="📱 WhatsApp", url="https://t.me/duishobaevislam01"),
        InlineKeyboardButton(text="💬 Telegram", url="https://t.me/duishobaevislam01"),
        InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start")
    )
    await query.message.edit_caption(
        caption="Вы можете связаться с нами через: \n📧 Email, \n📱 WhatsApp \n💬 Telegram",
        reply_markup=keyboard.adjust(1).as_markup()
    )


@start_functions_private_router.message(Command("contact_us"))
async def contact_us_message(query: types.Message):
    """Обработчик для кнопки 'contact_us'"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="📧 Email", url="https://t.me/duishobaevislam01"),
        InlineKeyboardButton(text="📱 WhatsApp", url="https://t.me/duishobaevislam01"),
        InlineKeyboardButton(text="💬 Telegram", url="https://t.me/duishobaevislam01"),
        InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start_")
    )
    await query.reply(
        text="Вы можете связаться с нами через: \n📧 Email, \n📱 WhatsApp \n💬 Telegram",
        reply_markup=keyboard.adjust(1).as_markup()
    )

