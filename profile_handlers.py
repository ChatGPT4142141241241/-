from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_session, User, Hero, Build, Note
import json
from datetime import datetime

router = Router()

class ProfileStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_game_id = State()
    waiting_for_note = State()
    waiting_for_build_name = State()
    waiting_for_build_description = State()

# Обработчик создания профиля
@router.callback_query(F.data == "create_profile")
async def create_profile(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileStates.waiting_for_nickname)
    await callback.message.edit_text(
        "📝 Создание профиля\n\n"
        "Введите ваш игровой никнейм:"
    )

# Обработчик получения никнейма
@router.message(ProfileStates.waiting_for_nickname)
async def process_nickname(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await state.set_state(ProfileStates.waiting_for_game_id)
    await message.answer(
        "Теперь введите ваш игровой ID:"
    )

# Обработчик получения ID
@router.message(ProfileStates.waiting_for_game_id)
async def process_game_id(message: Message, state: FSMContext):
    try:
        game_id = int(message.text)
        data = await state.get_data()
        
        session = get_session()
        user = User(
            telegram_id=message.from_user.id,
            nickname=data['nickname'],
            game_id=game_id,
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()
        
        await state.clear()
        await message.answer(
            "✅ Профиль успешно создан!\n\n"
            f"Ник: {data['nickname']}\n"
            f"ID: {game_id}"
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат ID. Пожалуйста, введите числовой ID:"
        )

# Обработчик избранных героев
@router.callback_query(F.data == "favorites")
async def show_favorites(callback: CallbackQuery):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not user:
        await callback.message.edit_text(
            "❌ Профиль не найден. Создайте профиль, чтобы добавлять героев в избранное."
        )
        return
    
    favorites = json.loads(user.favorites) if user.favorites else []
    heroes = session.query(Hero).filter(Hero.id.in_(favorites)).all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for hero in heroes:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{hero.name} ({hero.role})",
                callback_data=f"hero_{hero.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="profile")
    ])
    
    await callback.message.edit_text(
        "⭐️ Избранные герои\n\n"
        "Выберите героя для просмотра:",
        reply_markup=keyboard
    )

# Обработчик сборок
@router.callback_query(F.data == "builds")
async def show_builds(callback: CallbackQuery):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not user:
        await callback.message.edit_text(
            "❌ Профиль не найден. Создайте профиль, чтобы создавать сборки."
        )
        return
    
    builds = session.query(Build).filter_by(user_id=user.id).all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for build in builds:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=build.name,
                callback_data=f"build_{build.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="➕ Создать сборку", callback_data="create_build"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="profile")
    ])
    
    await callback.message.edit_text(
        "🎯 Сборки\n\n"
        "Выберите сборку для просмотра:",
        reply_markup=keyboard
    )

# Обработчик создания сборки
@router.callback_query(F.data == "create_build")
async def create_build(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileStates.waiting_for_build_name)
    await callback.message.edit_text(
        "📝 Создание сборки\n\n"
        "Введите название сборки:"
    )

# Обработчик получения названия сборки
@router.message(ProfileStates.waiting_for_build_name)
async def process_build_name(message: Message, state: FSMContext):
    await state.update_data(build_name=message.text)
    await state.set_state(ProfileStates.waiting_for_build_description)
    await message.answer(
        "Теперь введите описание сборки:"
    )

# Обработчик получения описания сборки
@router.message(ProfileStates.waiting_for_build_description)
async def process_build_description(message: Message, state: FSMContext):
    data = await state.get_data()
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    build = Build(
        user_id=user.id,
        name=data['build_name'],
        description=message.text,
        created_at=datetime.now()
    )
    session.add(build)
    session.commit()
    
    await state.clear()
    await message.answer(
        "✅ Сборка успешно создана!\n\n"
        f"Название: {data['build_name']}\n"
        f"Описание: {message.text}"
    )

# Обработчик заметок
@router.callback_query(F.data == "notes")
async def show_notes(callback: CallbackQuery):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not user:
        await callback.message.edit_text(
            "❌ Профиль не найден. Создайте профиль, чтобы создавать заметки."
        )
        return
    
    notes = session.query(Note).filter_by(user_id=user.id).all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for note in notes:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=note.title,
                callback_data=f"note_{note.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="➕ Создать заметку", callback_data="create_note"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="profile")
    ])
    
    await callback.message.edit_text(
        "📝 Заметки\n\n"
        "Выберите заметку для просмотра:",
        reply_markup=keyboard
    )

# Обработчик создания заметки
@router.callback_query(F.data == "create_note")
async def create_note(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileStates.waiting_for_note)
    await callback.message.edit_text(
        "📝 Создание заметки\n\n"
        "Введите текст заметки:"
    )

# Обработчик получения текста заметки
@router.message(ProfileStates.waiting_for_note)
async def process_note(message: Message, state: FSMContext):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    note = Note(
        user_id=user.id,
        title=message.text[:30] + "..." if len(message.text) > 30 else message.text,
        content=message.text,
        created_at=datetime.now()
    )
    session.add(note)
    session.commit()
    
    await state.clear()
    await message.answer(
        "✅ Заметка успешно создана!\n\n"
        f"Текст: {message.text}"
    ) 