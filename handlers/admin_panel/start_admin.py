from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import get_admins, get_admin, get_admin_by_id, remove_admin, orm_add_admin, orm_add_supplier, \
    orm_get_suppliers, orm_get_supplier_by_id, orm_delete_supplier, get_total_users, get_total_admins, \
    get_total_suppliers
from filter.chat_types import ChatTypeFilter
from keyboard.inline import start_admin_inline_keyboard, return_admin_panel_functions_keyboard, get_cancel_keyboard

admin_private_router = Router()
admin_private_router.message.filter(ChatTypeFilter(["private"]))

# Приветственное сообщение
admin_message = (
    "Добро пожаловать в панель администратора! 🌟"
)


@admin_private_router.message(Command("start_admin"))
async def start_cmd(message: types.Message, session: AsyncSession):
    # Получаем список администраторов из базы данных
    users = await get_admins(session)
    admin = message.from_user.id

    # Проверяем, является ли пользователь администратором
    if admin in users:
        keyboard = start_admin_inline_keyboard()
        await message.answer_photo(
            photo=types.FSInputFile('media/img.png'),
            caption=f"{admin_message} \n"
                    f"{message.from_user.full_name}! 😊",
            reply_markup=keyboard
        )
    else:
        await message.answer("Эта команда доступна только администраторам.")


@admin_private_router.callback_query((F.data.startswith('start_admin')))
async def start_command_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    try:
        user_id = query.from_user.id
        admins = await get_admins(session)  # Получаем список ID администраторов из базы

        if user_id not in admins:
            await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
            return

        keyboard = start_admin_inline_keyboard()

        await query.message.edit_caption(
            caption=f"{admin_message}",
            reply_markup=keyboard
        )
    except Exception as e:
        await query.answer(f"Произошла ошибка: {str(e)}", show_alert=True)


@admin_private_router.callback_query((F.data == 'list_admins'))
async def bot_list_admins_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    try:
        # Проверяем, является ли пользователь администратором
        user_id = query.from_user.id
        admins = await get_admins(session)  # Получаем список ID администраторов из базы

        if user_id not in admins:
            await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
            return

        users = await get_admin(session)  # Получаем список администраторов из базы данных
        keyboard = InlineKeyboardBuilder()

        if users:
            for user in users:
                keyboard.add(InlineKeyboardButton(text=user.name, callback_data=f"admin_{user.user_id}"))
            keyboard.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start_admin"))
        else:
            await query.answer("Нет администраторов в системе.", show_alert=True)
            return

        if not query.message or not query.message.photo:
            await query.answer("Сообщение недоступно для редактирования.", show_alert=True)
            return

        await query.message.edit_caption(
            caption="Список администраторов:",
            reply_markup=keyboard.adjust(1).as_markup()
        )
    except Exception as e:
        await query.answer(f"Произошла ошибка: {str(e)}", show_alert=True)


@admin_private_router.callback_query((F.data.startswith('admin_')))
async def info_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    try:
        # Проверяем, является ли пользователь администратором
        user_id = query.from_user.id
        admins = await get_admins(session)  # Получаем список ID администраторов из базы

        if user_id not in admins:
            await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
            return

        # Проверка на корректность данных
        if not query.data or len(query.data.split('_')) < 2:
            await query.answer("Некорректные данные.", show_alert=True)
            return

        admin_id = int(query.data.split('_')[1])  # Извлекаем user_id администратора из callback_data
        admin = await get_admin_by_id(session, admin_id)  # Получаем информацию о пользователе из базы данных

        if admin:
            admin_message = f"Информация о админе:\n" \
                            f"Имя: {admin.name}\n" \
                            f"Username: {admin.username}\n" \
                            f"ID: {admin.user_id}\n"

            keyboard = InlineKeyboardBuilder()
            keyboard.add(
                InlineKeyboardButton(text="Удалить администратора", callback_data=f"delete_admin_{admin.user_id}"))
            keyboard.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start_admin"))

            # Проверка, есть ли сообщение и можно ли его редактировать
            if not query.message or not query.message.photo:
                await query.answer("Сообщение недоступно для редактирования.", show_alert=True)
                return

            await query.message.edit_caption(
                caption=admin_message,
                reply_markup=keyboard.adjust(1, 1).as_markup()
            )
        else:
            await query.answer("Не удалось найти информацию о пользователе.", show_alert=True)
    except ValueError:
        await query.answer("Некорректный ID администратора.", show_alert=True)
    except Exception as e:
        await query.answer(f"Произошла ошибка: {str(e)}", show_alert=True)


@admin_private_router.callback_query((F.data.startswith('delete_admin_')))
async def delete_admin_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    try:
        user_id = query.from_user.id
        admins = await get_admins(session)  # Получаем список ID администраторов из базы

        if user_id not in admins:
            await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
            return

        # Извлечение ID администратора из callback_data
        admin_id = int(query.data.split('_')[2])

        # Проверка: удаляет ли администратор самого себя
        if query.from_user.id == admin_id:
            await query.answer("Вы не можете удалить самого себя.", show_alert=True)
            return

        # Проверка: существует ли администратор
        admin = await get_admin_by_id(session, admin_id)
        if not admin:
            await query.answer("Администратор не найден.", show_alert=True)
            return

        # Удаляем администратора
        await remove_admin(session, admin_id)

        # Обновляем сообщение
        await query.message.edit_caption(
            caption=f"Администратор {admin.name} был успешно удален.",
            reply_markup=None  # Убираем клавиатуру после удаления
        )

    except ValueError:
        await query.answer("Некорректный ID администратора.", show_alert=True)
    except Exception as e:
        await query.answer(f"Произошла ошибка: {str(e)}", show_alert=True)


@admin_private_router.callback_query(F.data == "add_admin")
async def add_admin_info_bot(query: types.CallbackQuery, session: AsyncSession) -> None:
    user_id = query.from_user.id
    admins = await get_admins(session)

    if user_id not in admins:
        await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
        return

    await query.message.edit_caption(
        caption=(
            "🔹 Как добавить нового администратора? 🔹\n\n"
            "Для добавления нового администратора используйте команду в формате:\n"
            "/add_admin telegram_id name username\n\n"
            "Пример:\n"
            "/add_admin 123456789 JohnDoe johndoe123\n\n"
            "🔑 Как получить telegram_id нового администратора? 🔑\n"
            "1. Попросите нового администратора написать любое сообщение в чат с ботом @UserInfoToBot.\n"
            "2. Бот ответит ему его telegram_id.\n"
            "3. После этого вы сможете использовать полученный telegram_id для добавления нового администратора.\n\n"
            "💡 Важно! После получения telegram_id обязательно укажите также имя и username нового администратора.\n\n"
            "Введите команду с полученными данными, чтобы добавить нового администратора."
        ),
        reply_markup=return_admin_panel_functions_keyboard(),
    )


@admin_private_router.message(F.text.startswith("/add_admin"))
async def add_admin(message: types.Message, session: AsyncSession):
    try:
        # Получаем данные из команды /add_admin
        parts = message.text.split()

        # Проверяем правильность формата команды
        if len(parts) != 4:
            await message.answer("Неверный формат команды. Используйте: /add_admin telegram_id name username")
            return

        # Разбираем данные
        user_id_str, name, username = parts[1], parts[2], parts[3]

        # Проверка, что telegram_id - это число
        try:
            user_id = int(user_id_str)
        except ValueError:
            await message.answer("Неверный формат telegram_id. Он должен быть числом.")
            return

        # Проверка на пустые значения для name и username
        if not name or not username:
            await message.answer("Имя и username не могут быть пустыми.")
            return

        # Проверка, что отправитель является администратором
        sender_id = message.from_user.id
        admins = await get_admins(session)  # Получаем список администраторов из базы данных

        if sender_id not in admins:
            await message.answer("У вас нет прав для выполнения этой команды.")
            return

        # Проверяем, существует ли уже такой пользователь в базе данных
        existing_admin = await get_admin_by_id(session, user_id)

        if existing_admin:
            # Если администратор уже существует, обновляем его статус
            existing_admin.is_admin = True
            await session.commit()
            await message.answer(f"Администратор {name} уже существует, его статус был обновлен.")
        else:
            # Если администратора нет, добавляем нового
            await orm_add_admin(session, user_id, name, username)
            await message.answer(f"Администратор {name} был успешно добавлен.")

    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")


class SupplierForm(StatesGroup):
    waiting_for_name = State()  # Ожидаем название поставщика
    waiting_for_site_url = State()  # Ожидаем URL сайта поставщика


@admin_private_router.callback_query(F.data == "add_supplier")
async def add_supplier_start(query: types.CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    user_id = query.from_user.id
    admins = await get_admins(session)

    if user_id not in admins:
        await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
        return

    # Начинаем процесс добавления поставщика
    await state.set_state(SupplierForm.waiting_for_name)

    # Сохраняем ID сообщения для последующего удаления
    await state.update_data(message_id=query.message.message_id)

    await query.message.edit_caption(
        caption="🔹 **Добавление нового поставщика** 🔹\n\n"
                "Пожалуйста, введите название поставщика.",
        reply_markup=get_cancel_keyboard()
    )


@admin_private_router.message(SupplierForm.waiting_for_name)
async def process_supplier_name(message: types.Message, state: FSMContext) -> None:
    supplier_name = message.text.strip()

    if not supplier_name:
        await message.answer("Название поставщика не может быть пустым. Пожалуйста, введите название.")
        return

    # Сохраняем название поставщика в состоянии
    await state.update_data(supplier_name=supplier_name)

    # Удаляем старое сообщение
    user_data = await state.get_data()
    message_id = user_data.get('message_id')
    if message_id:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    # Переходим к следующему состоянию (ожидаем URL сайта)
    await state.set_state(SupplierForm.waiting_for_site_url)
    m = await message.answer("Теперь введите URL сайта поставщика.", reply_markup=get_cancel_keyboard())
    await state.update_data(message_id=m.message_id)
    await message.delete()


@admin_private_router.message(SupplierForm.waiting_for_site_url)
async def process_supplier_site_url(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    site_url = message.text.strip()

    if not site_url:
        await message.answer("URL сайта не может быть пустым. Пожалуйста, введите URL.")
        return

    # Получаем данные из состояния
    user_data = await state.get_data()
    supplier_name = user_data.get('supplier_name')

    # Добавляем нового поставщика в базу данных
    await orm_add_supplier(session, supplier_name, site_url)

    # Удаляем старое сообщение
    message_id = user_data.get('message_id')
    if message_id:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)


    # Завершаем процесс
    await state.clear()

    # Отправляем сообщение об успешном добавлении
    await message.answer(f"Поставщик '{supplier_name}' был успешно добавлен.", parse_mode=ParseMode.MARKDOWN,reply_markup=return_admin_panel_functions_keyboard())
    await message.delete()


@admin_private_router.callback_query(F.data == 'all_suppliers')
async def bot_all_suppliers_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    try:
        # Проверяем, является ли пользователь администратором
        user_id = query.from_user.id
        admins = await get_admins(session)  # Получаем список ID администраторов из базы

        if user_id not in admins:
            await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
            return

        suppliers = await orm_get_suppliers(session)
        keyboard = InlineKeyboardBuilder()

        if suppliers:
            for i in suppliers:
                keyboard.add(InlineKeyboardButton(text=i.title, callback_data=f"suppliers_{i.id}"))
            keyboard.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start_admin"))
        else:
            await query.answer("Нет поставщиков в системе.", show_alert=True)
            return

        if not query.message:
            await query.answer("Сообщение недоступно для редактирования.", show_alert=True)
            return

        # Если в сообщении есть фото, редактируем подпись
        if query.message.photo:
            await query.message.edit_caption(
                caption="Список поставщиков:",
                reply_markup=keyboard.adjust(1).as_markup()
            )
        else:
            # Если фото нет, редактируем только текст
            await query.message.edit_text(
                text="Список поставщиков:",
                reply_markup=keyboard.adjust(1).as_markup()
            )
    except Exception as e:
        await query.answer(f"Произошла ошибка: {str(e)}", show_alert=True)


@admin_private_router.callback_query(F.data.startswith('suppliers_'))
async def suppliers_info_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
    # Проверяем, является ли пользователь администратором
    user_id = query.from_user.id
    admins = await get_admins(session)  # Получаем список ID администраторов из базы

    if user_id not in admins:
        await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
        return

    # Извлекаем ID поставщика из callback_data
    supplier_id = query.data.split('_')[1]

    # Получаем информацию о поставщике из базы данных
    supplier = await orm_get_supplier_by_id(session, supplier_id)

    if supplier:
        # Создаем клавиатуру с кнопкой для удаления поставщика
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(text="Удалить поставщика", callback_data=f"delete_supplier_{supplier.id}")
        )
        keyboard.add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start_admin"))

        # Обновляем caption с информацией о поставщике
        await query.message.edit_caption(
            caption=f"Поставщик: {supplier.title}\nСайт: {supplier.site_url}\nДата создания: {supplier.created}\nДата обновления: {supplier.updated}",
            reply_markup=keyboard.adjust(1).as_markup()
        )
    else:
        await query.answer("Поставщик не найден.", show_alert=True)


@admin_private_router.callback_query(F.data.startswith('delete_supplier_'))
async def delete_supplier_callback_query(query: types.CallbackQuery, session: AsyncSession) -> None:
        user_id = query.from_user.id
        admins = await get_admins(session)  # Получаем список ID администраторов из базы

        if user_id not in admins:
            await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
            return

        # Извлекаем ID поставщика из callback_data
        supplier_id = query.data.split('_')[2]

        # Удаляем поставщика из базы данных
        await orm_delete_supplier(session, supplier_id)

        # Обновляем сообщение, чтобы отразить изменения
        await query.message.edit_caption(
            caption="Поставщик был успешно удален.",
            reply_markup=InlineKeyboardBuilder().add(InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="start_admin")).as_markup()
        )
        await query.answer("Поставщик успешно удален.", show_alert=True)


async def get_statistics(session: AsyncSession) -> str:
    total_users = await get_total_users(session)
    total_admins = await get_total_admins(session)
    total_suppliers = await get_total_suppliers(session)

    return (
        "📊 Статистика:\n"
        f"- Всего пользователей: {total_users}\n"
        f"- Администраторов: {total_admins}\n"
        f"- Поставщиков: {total_suppliers}\n"
    )

@admin_private_router.callback_query(F.data == "bot_statistics")
async def bot_statistics_info_bot(query: types.CallbackQuery, session: AsyncSession) -> None:
    user_id = query.from_user.id
    admins = await get_admins(session)

    if user_id not in admins:
        await query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
        return

    # Получаем статистику
    statistics_text = await get_statistics(session)

    # Отправляем ответ
    await query.message.edit_caption(
        caption=statistics_text,
        reply_markup=return_admin_panel_functions_keyboard(),
    )

