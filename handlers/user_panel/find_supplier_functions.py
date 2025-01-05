import asyncio
from aiogram import F, Router, types, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_suppliers, orm_get_supplier_by_id
from filter.chat_types import ChatTypeFilter
from handlers.ai_function import sent_prompt_and_get_response
from handlers.user_panel.start_functions import welcome_text
from keyboard.inline import get_cancel_keyboard, start_functions_keyboard

find_supplier_private_router = Router()
find_supplier_private_router.message.filter(ChatTypeFilter(['private']))


# Определяем состояния
class AiAssistanceState(StatesGroup):
    WaitingForReview = State()


# Обработка нажатия кнопки "Найти поставщика"
@find_supplier_private_router.callback_query(F.data == "find_supplier")
async def find_supplier_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    m = await query.message.edit_caption(
        caption="✍️ Пожалуйста, напишите, что вы хотите купить. Я подберу для вас подходящих поставщиков! 🔍",
        reply_markup=get_cancel_keyboard()
    )
    await state.update_data(message_id=m.message_id)
    await query.answer("Жду ваш запрос! 📝")
    await state.set_state(AiAssistanceState.WaitingForReview)


@find_supplier_private_router.callback_query(F.data.startswith("find_supplier2"))
async def find_supplier__callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    m = await query.message.answer_photo(
        photo=types.FSInputFile('media/img.png'),
        caption="✍️ Пожалуйста, напишите, что вы хотите купить. Я подберу для вас подходящих поставщиков! 🔍",
        reply_markup=get_cancel_keyboard()
    )
    await state.update_data(message_id=m.message_id)
    await query.answer("Жду ваш запрос! 📝")
    await state.set_state(AiAssistanceState.WaitingForReview)


# Обработка текста от пользователя
@find_supplier_private_router.message(AiAssistanceState.WaitingForReview)
async def find_supplier_help_request(message: types.Message, state: FSMContext, bot: Bot,session: AsyncSession):
    user_info = message.from_user.first_name or ""
    if message.from_user.last_name:
        user_info += f" {message.from_user.last_name}"
    if message.from_user.username:
        user_info += f" (@{message.from_user.username})"

    if message.text:
        # Подтверждение получения запроса
        processing_message = await message.answer(
            f"✅ Спасибо за запрос, {user_info}!\n"
            "⏳ Немного терпения — я ищу подходящих поставщиков для вас..."
        )

        try:
            data = await orm_get_suppliers(session)
            generated_help = sent_prompt_and_get_response(message.text, data)
        except Exception as e:
            generated_help = (
                "😔 Извините, я не смог обработать ваш запрос.\n"
                "Попробуйте снова или свяжитесь с поддержкой. 💬"
            )
            print(f"Ошибка генерации ответа: {e}")

        # Создание клавиатуры
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(text='↩️ Вернуться в главное меню', callback_data='start_'),
            InlineKeyboardButton(text='🔄 Новый запрос', callback_data='find_supplier2')
        )

        # Отправка ответа пользователю
        await bot.edit_message_text(
            chat_id=processing_message.chat.id,
            message_id=processing_message.message_id,
            text=f"📋 Результат поиска:\n\n{generated_help}",
            reply_markup=keyboard.adjust(1).as_markup(),
            parse_mode=ParseMode.MARKDOWN
        )

        # Удаление старого сообщения, если оно есть
        user_data = await state.get_data()
        message_id = user_data.get("message_id")

        if message_id:
            try:
                await bot.delete_message(message.chat.id, message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")

        # Очистка состояния
        await state.clear()

    else:
        # Если пользователь отправил что-то, кроме текста
        await message.reply(
            "⚠️ Пожалуйста, отправьте текстовый запрос, чтобы я мог помочь вам. 🙏"
        )


@find_supplier_private_router.callback_query(F.data == "cancel")
async def cancel(query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer("🚫 Действие отменено. Возвращаемся в главное меню.")

    # Проверяем, есть ли фотография в сообщении
    if query.message.photo:
        # Если есть фото, редактируем подпись
        await query.message.edit_caption(
            caption=welcome_text,
            reply_markup=start_functions_keyboard()
        )
    else:
        # Если фото нет, редактируем только текст
        await query.message.edit_text(
            text=welcome_text,
            reply_markup=start_functions_keyboard()
        )


@find_supplier_private_router.callback_query(F.data == "find_supplier_by_city")
async def find_supplier_by_city_callback_query(query: types.CallbackQuery, state: FSMContext,
                                               session: AsyncSession) -> None:
    await state.clear()
    suppliers = await orm_get_suppliers(session)
    builder = InlineKeyboardBuilder()
    for supplier in suppliers:
        builder.add(
            InlineKeyboardButton(text=supplier.address, callback_data=f"city_{supplier.id}")
        )
    builder.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start"))
    await query.message.edit_caption(
        caption="Пожалуйста, выберите адрес, который вам ближе.",
        reply_markup=builder.adjust(1).as_markup()  # Используем созданную клавиатуру
    )
    await query.answer("Жду ваш запрос! 📝")


@find_supplier_private_router.callback_query(F.data.startswith("city_"))
async def find_supplier_by_city_info_callback_query(query: types.CallbackQuery, state: FSMContext,
                                                    session: AsyncSession) -> None:
    # Извлекаем id поставщика из callback_data
    supplier_id = int(query.data.split("_")[1])

    # Получаем информацию о поставщике
    supplier = await orm_get_supplier_by_id(session, supplier_id=supplier_id)

    if supplier:
        builder = InlineKeyboardBuilder()

        # Добавляем кнопку с сайтом, если он существует и начинается с "https://"
        if supplier.site_url and supplier.site_url.startswith("https://"):
            builder.add(InlineKeyboardButton(text=supplier.title, url=supplier.site_url))

        # Кнопка для возврата в главное меню
        builder.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start"))

        supplier_info = (
            f"✨ Вот информация о поставщике, который может вам помочь с покупкой! ✨\n\n"
            f"🛠 **Поставщик**: {supplier.title}\n"
            f"📍 **Адрес**: {supplier.address}\n"
            f"🌐 **Сайт**: {supplier.site_url if supplier.site_url else 'Нет сайта'}\n\n"
            f"Вы можете обратиться к этому поставщику для получения более подробной информации и оформления заказа."
        )

        await query.message.edit_caption(
            caption=supplier_info,
            reply_markup=builder.adjust(1).as_markup() ,
            parse_mode=ParseMode.MARKDOWN
        )
        await query.answer("Вот информация о поставщике! 📑")
    else:
        await query.answer("Извините, поставщик не найден. Попробуйте снова.")

