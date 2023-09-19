import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Text
from aiogram.filters.command import Command

from os import getenv

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(level=logging.INFO)
# Объект бота
TOKEN = getenv("BOT_TOKEN")
admin_id = 1059184359

# Диспетчер
dp = Dispatcher()

available_food_names = ['Cпагетти', 'Рис', 'Пельмени']
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]


class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()
    create_new_food = State()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):

    kb = [
        [types.KeyboardButton(text='Заказать еду')],
        [types.KeyboardButton(text='Написать в поддержку')],
        [types.KeyboardButton(text='Добавить новое блюдо')]
    ]
    kb2 = [
        [types.KeyboardButton(text='Заказать еду')],
        [types.KeyboardButton(text='Написать в поддержку')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    keyboard2 = types.ReplyKeyboardMarkup(keyboard=kb2, resize_keyboard=True)

    if message.from_user.id == admin_id:
        await message.answer("Добро пожаловать в наш магазин!", reply_markup=keyboard)
    else:
        await message.answer("Добро пожаловать в наш магазин!", reply_markup=keyboard2)
@dp.message(Text('Добавить новое блюдо'))
async def cmd_add_food(message: types.Message, state: FSMContext):
    if message.from_user.id == admin_id:
        await message.answer(f'Текущие блюда: {available_food_names}\n\nНапишите название блюда, которое хотели бы добавить')
        await state.set_state(OrderFood.create_new_food)
    else:
        await message.answer('Вы не имеете доступ к данной функции')

@dp.message(OrderFood.create_new_food)
async def creating(message: types.Message, state: FSMContext):

    await state.update_data(chosen_creating_food=message.text.lower())
    available_food_names.append(message.text.lower())
    food_type = await state.get_data()
    await message.answer(f'Вы выбрали: {message.text.title()}, теперь список выглядит так: {available_food_names}')
    await state.clear()


@dp.message(Text('Заказать еду'))
async def cmd_food(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardBuilder()
    for item in available_food_names:
        keyboard.add(types.KeyboardButton(text=item.title()))


    await message.answer(
        text="Выберите блюдо:",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(OrderFood.choosing_food_name)

@dp.message(OrderFood.choosing_food_name)
async def food_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_food_names:
        await message.answer('Блюда нет')
        return
    keyboard2 = ReplyKeyboardBuilder()
    for item in available_food_sizes:
        keyboard2.add(types.KeyboardButton(text=item))

    await message.answer('Спасибо за выбор!', reply_markup=keyboard2.as_markup(resize_keyboard=True))
    await state.update_data(chosen_food=message.text.lower())
    await state.set_state(OrderFood.choosing_food_size)

@dp.message(OrderFood.choosing_food_size)
async def food_chosen_size(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}", reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()




# Запуск процесса поллинга новых апдейтов
async def main():
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())