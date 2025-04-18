from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_session, ShopItem, User, UserItem
from datetime import datetime

router = Router()

class ShopStates(StatesGroup):
    waiting_for_item_name = State()
    waiting_for_item_description = State()
    waiting_for_item_price = State()
    waiting_for_item_category = State()
    waiting_for_item_image = State()
    waiting_for_search = State()

# Обработчик просмотра магазина
@router.callback_query(F.data == "shop")
async def show_shop(callback: CallbackQuery):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Поиск товара", callback_data="search_item"),
            InlineKeyboardButton(text="📋 Категории", callback_data="show_categories")
        ]
    ])
    
    if user and user.is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_item")
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="menu")
    ])
    
    await callback.message.edit_text(
        "🛍 Магазин\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )

# Обработчик просмотра категорий
@router.callback_query(F.data == "show_categories")
async def show_categories(callback: CallbackQuery):
    session = get_session()
    categories = session.query(ShopItem.category).distinct().all()
    
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
        InlineKeyboardButton(text="🔙 Назад", callback_data="shop")
    ])
    
    await callback.message.edit_text(
        "📋 Категории товаров\n\n"
        "Выберите категорию:",
        reply_markup=keyboard
    )

# Обработчик просмотра товаров категории
@router.callback_query(F.data.startswith("category_"))
async def show_category_items(callback: CallbackQuery):
    category = callback.data.split("_", 1)[1]
    session = get_session()
    items = session.query(ShopItem).filter_by(category=category).all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for item in items:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{item.name} - {item.price} 💎",
                callback_data=f"item_{item.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="show_categories")
    ])
    
    await callback.message.edit_text(
        f"📋 Товары категории '{category}'\n\n"
        "Выберите товар для просмотра:",
        reply_markup=keyboard
    )

# Обработчик просмотра товара
@router.callback_query(F.data.startswith("item_"))
async def show_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    session = get_session()
    item = session.query(ShopItem).filter_by(id=item_id).first()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not item:
        await callback.message.edit_text("❌ Товар не найден")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    if user:
        user_item = session.query(UserItem).filter_by(
            user_id=user.id,
            item_id=item.id
        ).first()
        
        if not user_item:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"Купить за {item.price} 💎",
                    callback_data=f"buy_{item.id}"
                )
            ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"category_{item.category}")
    ])
    
    await callback.message.edit_text(
        f"🛍 {item.name}\n\n"
        f"Категория: {item.category}\n"
        f"Цена: {item.price} 💎\n\n"
        f"Описание:\n{item.description}",
        reply_markup=keyboard
    )

# Обработчик покупки товара
@router.callback_query(F.data.startswith("buy_"))
async def buy_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    session = get_session()
    item = session.query(ShopItem).filter_by(id=item_id).first()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not user:
        await callback.message.edit_text(
            "❌ Сначала создайте профиль, чтобы покупать товары"
        )
        return
    
    if user.diamonds < item.price:
        await callback.message.edit_text(
            "❌ Недостаточно алмазов для покупки"
        )
        return
    
    user.diamonds -= item.price
    user_item = UserItem(
        user_id=user.id,
        item_id=item.id,
        purchased_at=datetime.now()
    )
    session.add(user_item)
    session.commit()
    
    await callback.message.edit_text(
        "✅ Товар успешно куплен!\n\n"
        f"Название: {item.name}\n"
        f"Цена: {item.price} 💎\n"
        f"Остаток алмазов: {user.diamonds} 💎"
    )

# Обработчик поиска товара
@router.callback_query(F.data == "search_item")
async def search_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ShopStates.waiting_for_search)
    await callback.message.edit_text(
        "🔍 Поиск товара\n\n"
        "Введите название товара для поиска:"
    )

# Обработчик получения поискового запроса
@router.message(ShopStates.waiting_for_search)
async def process_search(message: Message, state: FSMContext):
    search_query = message.text.lower()
    session = get_session()
    items = session.query(ShopItem).filter(
        ShopItem.name.ilike(f"%{search_query}%")
    ).all()
    
    if not items:
        await message.answer(
            "❌ Товары не найдены. Попробуйте изменить поисковый запрос."
        )
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for item in items:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{item.name} - {item.price} 💎",
                callback_data=f"item_{item.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="shop")
    ])
    
    await state.clear()
    await message.answer(
        f"🔍 Результаты поиска по запросу '{message.text}'\n\n"
        "Выберите товар для просмотра:",
        reply_markup=keyboard
    )

# Обработчик добавления товара
@router.callback_query(F.data == "add_item")
async def add_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ShopStates.waiting_for_item_name)
    await callback.message.edit_text(
        "📝 Добавление товара\n\n"
        "Введите название товара:"
    )

# Обработчик получения названия товара
@router.message(ShopStates.waiting_for_item_name)
async def process_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ShopStates.waiting_for_item_description)
    await message.answer(
        "Теперь введите описание товара:"
    )

# Обработчик получения описания товара
@router.message(ShopStates.waiting_for_item_description)
async def process_item_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ShopStates.waiting_for_item_price)
    await message.answer(
        "Теперь введите цену товара в алмазах:"
    )

# Обработчик получения цены товара
@router.message(ShopStates.waiting_for_item_price)
async def process_item_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await state.set_state(ShopStates.waiting_for_item_category)
        await message.answer(
            "Теперь введите категорию товара:"
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат цены. Пожалуйста, введите число:"
        )

# Обработчик получения категории товара
@router.message(ShopStates.waiting_for_item_category)
async def process_item_category(message: Message, state: FSMContext):
    data = await state.get_data()
    session = get_session()
    
    item = ShopItem(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        category=message.text,
        created_at=datetime.now()
    )
    session.add(item)
    session.commit()
    
    await state.clear()
    await message.answer(
        "✅ Товар успешно добавлен!\n\n"
        f"Название: {data['name']}\n"
        f"Категория: {message.text}\n"
        f"Цена: {data['price']} 💎\n"
        f"Описание: {data['description']}"
    ) 