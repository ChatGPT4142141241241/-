from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import get_session, User, Hero, Term, QuizQuestion, ShopItem
import json
from datetime import datetime

router = Router()

# Обработчик раздела "Герои"
@router.callback_query(F.data == "heroes")
async def show_heroes(callback: CallbackQuery):
    session = get_session()
    heroes = session.query(Hero).all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for hero in heroes:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{hero.name} ({hero.role})",
                callback_data=f"hero_{hero.id}"
            )
        ])
    
    await callback.message.edit_text(
        "Выберите героя:",
        reply_markup=keyboard
    )

# Обработчик просмотра героя
@router.callback_query(F.data.startswith("hero_"))
async def show_hero(callback: CallbackQuery):
    hero_id = int(callback.data.split("_")[1])
    session = get_session()
    hero = session.query(Hero).filter_by(id=hero_id).first()
    
    if hero:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="heroes")]
        ])
        
        await callback.message.edit_text(
            f"🏆 {hero.name}\n\n"
            f"Роль: {hero.role}\n"
            f"Сложность: {hero.difficulty}\n"
            f"Винрейт: {hero.win_rate}%\n"
            f"Тир: {hero.tier}\n\n"
            f"Гайд:\n{hero.guide}",
            reply_markup=keyboard
        )

# Обработчик раздела "Тир-лист"
@router.callback_query(F.data == "tier_list")
async def show_tier_list(callback: CallbackQuery):
    session = get_session()
    heroes = session.query(Hero).order_by(Hero.tier).all()
    
    tier_s = [h for h in heroes if h.tier == "S"]
    tier_a = [h for h in heroes if h.tier == "A"]
    tier_b = [h for h in heroes if h.tier == "B"]
    
    text = "🏆 Тир-лист 2025\n\n"
    text += "S-тир:\n" + "\n".join([f"• {h.name}" for h in tier_s]) + "\n\n"
    text += "A-тир:\n" + "\n".join([f"• {h.name}" for h in tier_a]) + "\n\n"
    text += "B-тир:\n" + "\n".join([f"• {h.name}" for h in tier_b])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

# Обработчик раздела "Словарь"
@router.callback_query(F.data == "dictionary")
async def show_dictionary(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск", callback_data="search_term")],
        [InlineKeyboardButton(text="🔤 Алфавит", callback_data="alphabet")],
        [InlineKeyboardButton(text="📁 Категории", callback_data="categories")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        "📘 Словарь терминов и сленга\n\n"
        "Выберите способ поиска:",
        reply_markup=keyboard
    )

# Обработчик раздела "Профиль"
@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not user:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать профиль", callback_data="create_profile")]
        ])
        await callback.message.edit_text(
            "👤 Профиль не найден\n\n"
            "Создайте профиль, чтобы сохранять избранных героев, сборки и заметки.",
            reply_markup=keyboard
        )
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ Избранные герои", callback_data="favorites")],
        [InlineKeyboardButton(text="🎯 Сборки", callback_data="builds")],
        [InlineKeyboardButton(text="📝 Заметки", callback_data="notes")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        f"👤 Профиль\n\n"
        f"Ник: {user.nickname}\n"
        f"ID: {user.game_id}\n"
        f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}",
        reply_markup=keyboard
    )

# Обработчик раздела "Магазин"
@router.callback_query(F.data == "shop")
async def show_shop(callback: CallbackQuery):
    session = get_session()
    items = session.query(ShopItem).filter_by(status="approved").all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Алмазы", callback_data="shop_diamonds")],
        [InlineKeyboardButton(text="🎨 Скины", callback_data="shop_skins")],
        [InlineKeyboardButton(text="👤 Аккаунты", callback_data="shop_accounts")],
        [InlineKeyboardButton(text="🧙‍♂️ Услуги", callback_data="shop_services")],
        [InlineKeyboardButton(text="📦 Выставить товар", callback_data="add_item")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        "🛍 Магазин\n\n"
        "⚠️ Все сделки проходят через пользователей. Бот не несёт ответственности за передачу товаров. Будьте осторожны!",
        reply_markup=keyboard
    )

# Обработчик возврата в главное меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
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
    
    await callback.message.edit_text(
        "Добро пожаловать в ML Helper AI! 🎮\n\n"
        "Выберите раздел в меню ниже:",
        reply_markup=keyboard
    ) 