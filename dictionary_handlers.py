from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_session, DictionaryTerm, User
from datetime import datetime

router = Router()

class DictionaryStates(StatesGroup):
    waiting_for_term = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_search = State()

# Обработчик просмотра словаря
@router.callback_query(F.data == "dictionary")
async def show_dictionary(callback: CallbackQuery):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Поиск термина", callback_data="search_term"),
            InlineKeyboardButton(text="📋 Категории", callback_data="show_categories")
        ]
    ])
    
    if user and user.is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="➕ Добавить термин", callback_data="add_term")
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="menu")
    ])
    
    await callback.message.edit_text(
        "📚 Словарь терминов\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )

# Обработчик просмотра категорий
@router.callback_query(F.data == "show_categories")
async def show_categories(callback: CallbackQuery):
    session = get_session()
    categories = session.query(DictionaryTerm.category).distinct().all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for category in categories:
        if category[0]:  # Проверяем, что категория не пустая
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=category[0],
                    callback_data=f"category_{category[0]}"
                )
            ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="dictionary")
    ])
    
    await callback.message.edit_text(
        "📋 Категории терминов\n\n"
        "Выберите категорию:",
        reply_markup=keyboard
    )

# Обработчик просмотра терминов категории
@router.callback_query(F.data.startswith("category_"))
async def show_category_terms(callback: CallbackQuery):
    category = callback.data.split("_", 1)[1]
    session = get_session()
    terms = session.query(DictionaryTerm).filter_by(category=category).all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for term in terms:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=term.term,
                callback_data=f"term_{term.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="show_categories")
    ])
    
    await callback.message.edit_text(
        f"📋 Термины категории '{category}'\n\n"
        "Выберите термин для просмотра:",
        reply_markup=keyboard
    )

# Обработчик просмотра термина
@router.callback_query(F.data.startswith("term_"))
async def show_term(callback: CallbackQuery):
    term_id = int(callback.data.split("_")[1])
    session = get_session()
    term = session.query(DictionaryTerm).filter_by(id=term_id).first()
    
    if not term:
        await callback.message.edit_text("❌ Термин не найден")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"category_{term.category}")]
    ])
    
    await callback.message.edit_text(
        f"📚 {term.term}\n\n"
        f"Категория: {term.category}\n\n"
        f"Описание:\n{term.description}",
        reply_markup=keyboard
    )

# Обработчик поиска термина
@router.callback_query(F.data == "search_term")
async def search_term(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DictionaryStates.waiting_for_search)
    await callback.message.edit_text(
        "🔍 Поиск термина\n\n"
        "Введите название термина для поиска:"
    )

# Обработчик получения поискового запроса
@router.message(DictionaryStates.waiting_for_search)
async def process_search(message: Message, state: FSMContext):
    search_query = message.text.lower()
    session = get_session()
    terms = session.query(DictionaryTerm).filter(
        DictionaryTerm.term.ilike(f"%{search_query}%")
    ).all()
    
    if not terms:
        await message.answer(
            "❌ Термины не найдены. Попробуйте изменить поисковый запрос."
        )
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for term in terms:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{term.term} ({term.category})",
                callback_data=f"term_{term.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="dictionary")
    ])
    
    await state.clear()
    await message.answer(
        f"🔍 Результаты поиска по запросу '{message.text}'\n\n"
        "Выберите термин для просмотра:",
        reply_markup=keyboard
    )

# Обработчик добавления термина
@router.callback_query(F.data == "add_term")
async def add_term(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DictionaryStates.waiting_for_term)
    await callback.message.edit_text(
        "📝 Добавление термина\n\n"
        "Введите название термина:"
    )

# Обработчик получения названия термина
@router.message(DictionaryStates.waiting_for_term)
async def process_term(message: Message, state: FSMContext):
    await state.update_data(term=message.text)
    await state.set_state(DictionaryStates.waiting_for_description)
    await message.answer(
        "Теперь введите описание термина:"
    )

# Обработчик получения описания термина
@router.message(DictionaryStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(DictionaryStates.waiting_for_category)
    await message.answer(
        "Теперь введите категорию термина:"
    )

# Обработчик получения категории термина
@router.message(DictionaryStates.waiting_for_category)
async def process_category(message: Message, state: FSMContext):
    data = await state.get_data()
    session = get_session()
    
    term = DictionaryTerm(
        term=data['term'],
        description=data['description'],
        category=message.text,
        created_at=datetime.now()
    )
    session.add(term)
    session.commit()
    
    await state.clear()
    await message.answer(
        "✅ Термин успешно добавлен!\n\n"
        f"Название: {data['term']}\n"
        f"Категория: {message.text}\n"
        f"Описание: {data['description']}"
    ) 