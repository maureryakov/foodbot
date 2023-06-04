import logging
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# Установка токена телеграм-бота
BOT_TOKEN = '2102525803:AAG8jb3_w3J+++++++++++++++++++++++++'

# Установка токена OpenAI
OPENAI_API_KEY = 'sk-aP1CnWG5hGMrDH2XQWLPT3Bl_____________________-'

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Клавиатура для выбора действий
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Получить рекомендации по питанию')],
        [KeyboardButton(text='Отмена')],
    ],
    resize_keyboard=True
)


class UserInput(StatesGroup):
    age = State()
    weight = State()
    height = State()
    recommendations = State()


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply('Привет! Я бот, который дает рекомендации по питанию. '
                        'Для начала, пожалуйста, введи свой возраст:')
    await UserInput.age.set()


# Обработчик ввода возраста
@dp.message_handler(state=UserInput.age)
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    await state.update_data(age=age)
    await message.reply('Отлично! Теперь введи свой вес (в килограммах):')
    await UserInput.weight.set()


# Обработчик ввода веса
@dp.message_handler(state=UserInput.weight)
async def process_weight(message: types.Message, state: FSMContext):
    weight = message.text
    await state.update_data(weight=weight)
    await message.reply('Хорошо! Введи свой рост (в сантиметрах):')
    await UserInput.height.set()


# Обработчик ввода роста
@dp.message_handler(state=UserInput.height)
async def process_height(message: types.Message, state: FSMContext):
    height = message.text
    await state.update_data(height=height)

    # Получение данных пользователя
    user_data = await state.get_data()
    age = user_data['age']
    weight = user_data['weight']
    height = user_data['height']

    # Получение рекомендаций от OpenAI
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=f"Я {age} лет, мой вес {weight} кг, а рост {height} см. "
               f"Что мне следует есть, чтобы быть здоровым?",
        max_tokens=860,
        n=1,
        stop=None,
        temperature=0.7
    )

    recommendations = response.choices[0].text.strip()

    await state.update_data(recommendations=recommendations)
    await message.reply(f"Вот рекомендации по питанию:\n\n{recommendations}",
                        reply_markup=menu_keyboard)
    await UserInput.recommendations.set()


# Обработчик выбора действий из меню
@dp.message_handler(state=UserInput.recommendations)
async def process_menu(message: types.Message):
    if message.text == 'Получить рекомендации по питанию':
        await message.reply('Отлично! Пожалуйста, введи свой возраст:')
        await UserInput.age.set()
    elif message.text == 'Отмена':
        await message.reply('До свидания!', reply_markup=types.ReplyKeyboardRemove())
        await dp.current_state().reset_state()


if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
