from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Рассчитать'), KeyboardButton(text='Информация')]],
    resize_keyboard=True)


inline_choices = InlineKeyboardMarkup()
bt = InlineKeyboardButton(text='Рассчитать норму калорий',callback_data='calories')
bt2 = InlineKeyboardButton(text='Формулы расчёта',callback_data='formulas')
inline_choices.row(bt, bt2)



@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=inline_choices)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('calories = 10 * weight + 6.25 * growth - 5 * age - 161')


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await UserState.growth.set()
    await message.answer('Введите свой рост:')


@dp.message_handler(state=UserState.growth)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await UserState.weight.set()
    await message.answer('Введите свой вес:')


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f'Ваша норма калорий: {calories:.2f}')
    await state.finish()


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup= menu)

@dp.message_handler()
async def all_message(message):
    await message.answer('Ввeдите команду /start,что бы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
