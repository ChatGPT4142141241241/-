import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
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

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать в ML Helper AI! 🎮\n\n"
        "Выберите раздел в меню ниже:",
        reply_markup=get_main_menu()
    )

# Команда /admin
@dp.message(Command("admin"))
async def admin_handler(message: Message):
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

# Хендлер для всех callback-кнопок
@dp.callback_query(F.data.in_([
    "heroes", "tier_list", "dictionary", "legends", 
    "profile", "daily_tip", "quiz", "shop"
]))
async def handle_callbacks(callback: CallbackQuery):
    await callback.answer(f"Вы выбрали: {callback.data}", show_alert=True)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
