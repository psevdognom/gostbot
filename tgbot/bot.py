import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from tgbot.settings import API_TOKEN
from tgbot.parse_tools import get_search_list_db


class GostStates(StatesGroup):
    """FSM states for the conversation."""
    choosing = State()
    typing_reply = State()
    typing_choice = State()


reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Поиск')]],
    one_time_keyboard=True,
    resize_keyboard=True
)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


async def start(message: Message, state: FSMContext):
    await message.answer(
        "Приветвую, я бот, могу искать госты по их ключевым словам. ",
        reply_markup=reply_keyboard)
    await state.set_state(GostStates.choosing)


async def search_gost(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(search_string=text)
    await message.answer('Введите номер, словао для поиска')
    await state.set_state(GostStates.typing_reply)


async def custom_choice(message: Message, state: FSMContext):
    await message.answer('Alright, please send me the category first, '
                         'for example "Most impressive skill"')
    await state.set_state(GostStates.typing_choice)


async def received_information(message: Message, state: FSMContext):
    text = message.text
    gost_list = get_search_list_db(text)

    await state.update_data(search_string=None)
    await message.answer('Вот все что удалось найти',
                         reply_markup=reply_keyboard)
    for gost in gost_list:
        await message.answer(gost.name +
                             '\n' +
                             gost.description,
                             reply_markup=reply_keyboard)

    await state.set_state(GostStates.choosing)


async def done(message: Message, state: FSMContext):
    await state.clear()


async def main():
    # Create the Bot and Dispatcher
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(start, Command('start'))
    dp.message.register(
        search_gost,
        StateFilter(GostStates.choosing),
        F.text.regexp(r'^(Поиск)$')
    )
    dp.message.register(
        search_gost,
        StateFilter(GostStates.typing_choice),
        F.text,
        ~F.text.startswith('/'),
        ~F.text.regexp(r'^Done$')
    )
    dp.message.register(
        received_information,
        StateFilter(GostStates.typing_reply),
        F.text,
        ~F.text.startswith('/'),
        ~F.text.regexp(r'^Done$')
    )
    dp.message.register(
        done,
        F.text.regexp(r'^Done$')
    )

    # Start the Bot with polling
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())