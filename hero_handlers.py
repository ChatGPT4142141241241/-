from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_session, Hero, Build, User, FavoriteHero
import json
from datetime import datetime

router = Router()

class HeroStates(StatesGroup):
    waiting_for_build_items = State()
    waiting_for_build_description = State()

# Обработчик просмотра героя
@router.callback_query(F.data.startswith("hero_"))
async def show_hero(callback: CallbackQuery):
    hero_id = int(callback.data.split("_")[1])
    session = get_session()
    hero = session.query(Hero).filter_by(id=hero_id).first()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not hero:
        await callback.message.edit_text("❌ Герой не найден")
        return
    
    # Проверяем, добавлен ли герой в избранное
    is_favorite = False
    if user:
        favorite = session.query(FavoriteHero).filter_by(
            user_id=user.id,
            hero_id=hero.id
        ).first()
        is_favorite = favorite is not None
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⭐️ Добавить в избранное" if not is_favorite else "⭐️ Удалить из избранного",
                callback_data=f"toggle_favorite_{hero.id}"
            )
        ],
        [
            InlineKeyboardButton(text="🎯 Сборки", callback_data=f"hero_builds_{hero.id}"),
            InlineKeyboardButton(text="📖 Гайд", callback_data=f"hero_guide_{hero.id}")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="heroes")]
    ])
    
    await callback.message.edit_text(
        f"🏆 {hero.name}\n\n"
        f"Роль: {hero.role}\n"
        f"Сложность: {hero.difficulty}\n"
        f"Винрейт: {hero.win_rate}%\n"
        f"Тир: {hero.tier}\n\n"
        f"Описание:\n{hero.description}",
        reply_markup=keyboard
    )

# Обработчик добавления/удаления из избранного
@router.callback_query(F.data.startswith("toggle_favorite_"))
async def toggle_favorite(callback: CallbackQuery):
    hero_id = int(callback.data.split("_")[2])
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not user:
        await callback.message.edit_text(
            "❌ Сначала создайте профиль, чтобы добавлять героев в избранное"
        )
        return
    
    favorite = session.query(FavoriteHero).filter_by(
        user_id=user.id,
        hero_id=hero_id
    ).first()
    
    if favorite:
        session.delete(favorite)
        message = "✅ Герой удален из избранного"
    else:
        new_favorite = FavoriteHero(
            user_id=user.id,
            hero_id=hero_id,
            created_at=datetime.now()
        )
        session.add(new_favorite)
        message = "✅ Герой добавлен в избранное"
    
    session.commit()
    
    # Обновляем сообщение с информацией о герое
    hero = session.query(Hero).filter_by(id=hero_id).first()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⭐️ Удалить из избранного" if favorite else "⭐️ Добавить в избранное",
                callback_data=f"toggle_favorite_{hero.id}"
            )
        ],
        [
            InlineKeyboardButton(text="🎯 Сборки", callback_data=f"hero_builds_{hero.id}"),
            InlineKeyboardButton(text="📖 Гайд", callback_data=f"hero_guide_{hero.id}")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="heroes")]
    ])
    
    await callback.message.edit_text(
        f"🏆 {hero.name}\n\n"
        f"Роль: {hero.role}\n"
        f"Сложность: {hero.difficulty}\n"
        f"Винрейт: {hero.win_rate}%\n"
        f"Тир: {hero.tier}\n\n"
        f"Описание:\n{hero.description}",
        reply_markup=keyboard
    )

# Обработчик просмотра сборок героя
@router.callback_query(F.data.startswith("hero_builds_"))
async def show_hero_builds(callback: CallbackQuery):
    hero_id = int(callback.data.split("_")[2])
    session = get_session()
    hero = session.query(Hero).filter_by(id=hero_id).first()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not hero:
        await callback.message.edit_text("❌ Герой не найден")
        return
    
    builds = session.query(Build).filter_by(hero_id=hero_id).all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for build in builds:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{build.name} ({build.type})",
                callback_data=f"build_{build.id}"
            )
        ])
    
    if user:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="➕ Создать сборку",
                callback_data=f"create_build_{hero.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"hero_{hero.id}")
    ])
    
    await callback.message.edit_text(
        f"🎯 Сборки для {hero.name}\n\n"
        "Выберите сборку для просмотра:",
        reply_markup=keyboard
    )

# Обработчик создания сборки для героя
@router.callback_query(F.data.startswith("create_build_"))
async def create_hero_build(callback: CallbackQuery, state: FSMContext):
    hero_id = int(callback.data.split("_")[2])
    await state.set_state(HeroStates.waiting_for_build_items)
    await state.update_data(hero_id=hero_id)
    
    await callback.message.edit_text(
        "📝 Создание сборки\n\n"
        "Введите предметы сборки через запятую:"
    )

# Обработчик получения предметов сборки
@router.message(HeroStates.waiting_for_build_items)
async def process_build_items(message: Message, state: FSMContext):
    await state.update_data(items=message.text)
    await state.set_state(HeroStates.waiting_for_build_description)
    
    await message.answer(
        "Теперь введите описание сборки:"
    )

# Обработчик получения описания сборки
@router.message(HeroStates.waiting_for_build_description)
async def process_build_description(message: Message, state: FSMContext):
    data = await state.get_data()
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    build = Build(
        user_id=user.id,
        hero_id=data['hero_id'],
        items=data['items'],
        description=message.text,
        created_at=datetime.now()
    )
    session.add(build)
    session.commit()
    
    await state.clear()
    await message.answer(
        "✅ Сборка успешно создана!\n\n"
        f"Предметы: {data['items']}\n"
        f"Описание: {message.text}"
    )

# Обработчик просмотра гайда героя
@router.callback_query(F.data.startswith("hero_guide_"))
async def show_hero_guide(callback: CallbackQuery):
    hero_id = int(callback.data.split("_")[2])
    session = get_session()
    hero = session.query(Hero).filter_by(id=hero_id).first()
    
    if not hero:
        await callback.message.edit_text("❌ Герой не найден")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"hero_{hero.id}")]
    ])
    
    await callback.message.edit_text(
        f"📖 Гайд по {hero.name}\n\n"
        f"{hero.guide}",
        reply_markup=keyboard
    ) 