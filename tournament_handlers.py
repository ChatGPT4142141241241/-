from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_session, Tournament, User, TournamentParticipant
from datetime import datetime

router = Router()

class TournamentStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_start_date = State()
    waiting_for_rewards = State()
    waiting_for_team_name = State()
    waiting_for_team_members = State()

# Обработчик просмотра турниров
@router.callback_query(F.data == "tournaments")
async def show_tournaments(callback: CallbackQuery):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    # Получаем активные турниры
    active_tournaments = session.query(Tournament).filter(
        Tournament.status == "active"
    ).all()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for tournament in active_tournaments:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{tournament.name} ({tournament.start_date.strftime('%d.%m.%Y')})",
                callback_data=f"tournament_{tournament.id}"
            )
        ])
    
    if user and user.is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="➕ Создать турнир", callback_data="create_tournament")
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="menu")
    ])
    
    await callback.message.edit_text(
        "🏆 Турниры\n\n"
        "Выберите турнир для просмотра:",
        reply_markup=keyboard
    )

# Обработчик просмотра турнира
@router.callback_query(F.data.startswith("tournament_"))
async def show_tournament(callback: CallbackQuery):
    tournament_id = int(callback.data.split("_")[1])
    session = get_session()
    tournament = session.query(Tournament).filter_by(id=tournament_id).first()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not tournament:
        await callback.message.edit_text("❌ Турнир не найден")
        return
    
    # Проверяем, участвует ли пользователь в турнире
    is_participant = False
    if user:
        participant = session.query(TournamentParticipant).filter_by(
            user_id=user.id,
            tournament_id=tournament.id
        ).first()
        is_participant = participant is not None
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    if tournament.status == "active" and not is_participant:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="🎮 Участвовать",
                callback_data=f"join_tournament_{tournament.id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="📋 Участники", callback_data=f"participants_{tournament.id}"),
        InlineKeyboardButton(text="🏆 Награды", callback_data=f"rewards_{tournament.id}")
    ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="tournaments")
    ])
    
    await callback.message.edit_text(
        f"🏆 {tournament.name}\n\n"
        f"Дата начала: {tournament.start_date.strftime('%d.%m.%Y')}\n"
        f"Статус: {tournament.status}\n\n"
        f"Описание:\n{tournament.description}",
        reply_markup=keyboard
    )

# Обработчик участия в турнире
@router.callback_query(F.data.startswith("join_tournament_"))
async def join_tournament(callback: CallbackQuery, state: FSMContext):
    tournament_id = int(callback.data.split("_")[2])
    await state.set_state(TournamentStates.waiting_for_team_name)
    await state.update_data(tournament_id=tournament_id)
    
    await callback.message.edit_text(
        "🎮 Участие в турнире\n\n"
        "Введите название вашей команды:"
    )

# Обработчик получения названия команды
@router.message(TournamentStates.waiting_for_team_name)
async def process_team_name(message: Message, state: FSMContext):
    await state.update_data(team_name=message.text)
    await state.set_state(TournamentStates.waiting_for_team_members)
    await message.answer(
        "Теперь введите ID участников вашей команды через запятую:"
    )

# Обработчик получения участников команды
@router.message(TournamentStates.waiting_for_team_members)
async def process_team_members(message: Message, state: FSMContext):
    data = await state.get_data()
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    try:
        member_ids = [int(id.strip()) for id in message.text.split(",")]
        if len(member_ids) < 1 or len(member_ids) > 5:
            raise ValueError
        
        # Проверяем существование всех участников
        for member_id in member_ids:
            member = session.query(User).filter_by(id=member_id).first()
            if not member:
                raise ValueError
        
        # Создаем запись об участии
        participant = TournamentParticipant(
            user_id=user.id,
            tournament_id=data['tournament_id'],
            team_name=data['team_name'],
            team_members=message.text,
            registered_at=datetime.now()
        )
        session.add(participant)
        session.commit()
        
        await state.clear()
        await message.answer(
            "✅ Вы успешно зарегистрированы на турнир!\n\n"
            f"Название команды: {data['team_name']}\n"
            f"Участники: {message.text}"
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат ID участников. Пожалуйста, введите от 1 до 5 числовых ID через запятую:"
        )

# Обработчик просмотра участников турнира
@router.callback_query(F.data.startswith("participants_"))
async def show_participants(callback: CallbackQuery):
    tournament_id = int(callback.data.split("_")[1])
    session = get_session()
    participants = session.query(TournamentParticipant).filter_by(
        tournament_id=tournament_id
    ).all()
    
    text = "📋 Участники турнира:\n\n"
    for participant in participants:
        text += f"Команда: {participant.team_name}\n"
        text += f"Участники: {participant.team_members}\n"
        text += f"Дата регистрации: {participant.registered_at.strftime('%d.%m.%Y')}\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"tournament_{tournament_id}")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

# Обработчик просмотра наград турнира
@router.callback_query(F.data.startswith("rewards_"))
async def show_rewards(callback: CallbackQuery):
    tournament_id = int(callback.data.split("_")[1])
    session = get_session()
    tournament = session.query(Tournament).filter_by(id=tournament_id).first()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"tournament_{tournament_id}")]
    ])
    
    await callback.message.edit_text(
        f"🏆 Награды турнира {tournament.name}:\n\n"
        f"{tournament.rewards}",
        reply_markup=keyboard
    )

# Обработчик создания турнира
@router.callback_query(F.data == "create_tournament")
async def create_tournament(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TournamentStates.waiting_for_name)
    await callback.message.edit_text(
        "📝 Создание турнира\n\n"
        "Введите название турнира:"
    )

# Обработчик получения названия турнира
@router.message(TournamentStates.waiting_for_name)
async def process_tournament_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(TournamentStates.waiting_for_description)
    await message.answer(
        "Теперь введите описание турнира:"
    )

# Обработчик получения описания турнира
@router.message(TournamentStates.waiting_for_description)
async def process_tournament_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(TournamentStates.waiting_for_start_date)
    await message.answer(
        "Теперь введите дату начала турнира (дд.мм.гггг):"
    )

# Обработчик получения даты начала турнира
@router.message(TournamentStates.waiting_for_start_date)
async def process_tournament_start_date(message: Message, state: FSMContext):
    try:
        start_date = datetime.strptime(message.text, "%d.%m.%Y")
        await state.update_data(start_date=start_date)
        await state.set_state(TournamentStates.waiting_for_rewards)
        await message.answer(
            "Теперь введите награды турнира:"
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат даты. Пожалуйста, введите дату в формате дд.мм.гггг:"
        )

# Обработчик получения наград турнира
@router.message(TournamentStates.waiting_for_rewards)
async def process_tournament_rewards(message: Message, state: FSMContext):
    data = await state.get_data()
    session = get_session()
    
    tournament = Tournament(
        name=data['name'],
        description=data['description'],
        start_date=data['start_date'],
        rewards=message.text,
        status="active",
        created_at=datetime.now()
    )
    session.add(tournament)
    session.commit()
    
    await state.clear()
    await message.answer(
        "✅ Турнир успешно создан!\n\n"
        f"Название: {data['name']}\n"
        f"Дата начала: {data['start_date'].strftime('%d.%m.%Y')}\n"
        f"Описание: {data['description']}\n"
        f"Награды: {message.text}"
    ) 