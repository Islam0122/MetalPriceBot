from string import punctuation
from aiogram import F, types, Router, Bot
from aiogram.filters import CommandStart, Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession

from filter.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))
user_group_router.edited_message.filter(ChatTypeFilter(['group', 'supergroup']))

restricted_words = {
    'дурак', 'идиот', 'глупец', 'тупой', 'кретин', 'мразь', 'сволочь', 'урод',
    'дебил', 'придурок', 'засранец', 'тварь', 'скотина', 'гнида', 'сука',
    'падла', 'ублюдок', 'шлюха', 'проститутка', 'блядь', 'хрен', 'чмо',
    'козёл', 'баран', 'осёл', 'мерзавец', 'жопа', 'пизда', 'мудак', 'лох',
    'гандон', 'пидор', 'гей', 'тупица', 'недоумок', 'говно', 'задница',
    'петух', 'курва', 'шваль', 'хренов', 'шалава', 'говнюк', 'козлина'
}

@user_group_router.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()


def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))

# Проверка сообщений на запрещённые слова
@user_group_router.message()
async def check_restricted_words(message: types.Message):
    # Очистка текста от пунктуации и приведение к нижнему регистру
    cleaned_text = clean_text(message.text)
    message_words = set(cleaned_text.lower().split())  # Приведение всех слов к нижнему регистру

    # Преобразование запрещённых слов в нижний регистр
    restricted_words_lower = {word.lower() for word in restricted_words}

    # Проверка на наличие запрещённых слов
    if restricted_words_lower.intersection(message_words):
        await message.delete()  # Удаление сообщения
        await message.answer(
            f"⚠️ {message.from_user.first_name}, использование запрещённых слов недопустимо."
        )