import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создание клавиатуры главного меню
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🃏 Герои", callback_data="heroes"),
            InlineKeyboardButton(text="🧠 Тир-лист", callback_data="tier_list")
        ],
        [
            InlineKeyboardButton(text="📘 Словарь", callback_data="dictionary"),
            InlineKeyboardButton(text="🎭 Легенды", callback_data="legends")
        ],
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="☀️ Совет", callback_data="daily_tip")
        ],
        [
            InlineKeyboardButton(text="🎮 Викторина", callback_data="quiz"),
            InlineKeyboardButton(text="🛍 Магазин", callback_data="shop")
        ]
    ])
    return keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в ML Helper AI! 🎮\n\n"
        "Выберите раздел в меню ниже:",
        reply_markup=get_main_menu()
    )

# Обработчик команды /admin
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "Панель администратора:\n\n"
            "/add_hero - Добавить героя\n"
            "/update_guide - Обновить гайд\n"
            "/delete_hero - Удалить героя\n"
            "/add_term - Добавить термин\n"
            "/add_quiz - Добавить вопрос\n"
            "/ban_user - Забанить пользователя\n"
            "/stats - Статистика"
        )
    else:
        await message.answer("У вас нет доступа к этой команде.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 