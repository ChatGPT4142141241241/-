from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_session, QuizQuestion, User, UserQuiz
import json
from datetime import datetime
import random

router = Router()

class QuizStates(StatesGroup):
    waiting_for_answer = State()
    waiting_for_question = State()
    waiting_for_options = State()
    waiting_for_correct_answer = State()
    waiting_for_reward = State()

# Обработчик начала викторины
@router.callback_query(F.data == "quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if not user:
        await callback.message.edit_text(
            "❌ Сначала создайте профиль, чтобы участвовать в викторине"
        )
        return
    
    # Получаем случайный вопрос, который пользователь еще не отвечал
    answered_questions = session.query(UserQuiz.question_id).filter_by(user_id=user.id).all()
    answered_question_ids = [q[0] for q in answered_questions]
    
    question = session.query(QuizQuestion).filter(
        QuizQuestion.id.notin_(answered_question_ids)
    ).order_by(QuizQuestion.id).first()
    
    if not question:
        await callback.message.edit_text(
            "🎉 Поздравляем! Вы ответили на все вопросы викторины.\n\n"
            "Новые вопросы будут добавлены позже."
        )
        return
    
    options = json.loads(question.options)
    random.shuffle(options)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for i, option in enumerate(options):
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=option,
                callback_data=f"answer_{question.id}_{i}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="menu")
    ])
    
    await state.set_state(QuizStates.waiting_for_answer)
    await state.update_data(question_id=question.id, correct_answer=question.correct_answer)
    
    await callback.message.edit_text(
        f"❓ Вопрос:\n\n{question.question}\n\n"
        "Выберите правильный ответ:",
        reply_markup=keyboard
    )

# Обработчик ответа на вопрос
@router.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    question_id = int(data[1])
    answer_index = int(data[2])
    
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    question = session.query(QuizQuestion).filter_by(id=question_id).first()
    
    options = json.loads(question.options)
    user_answer = options[answer_index]
    is_correct = user_answer == question.correct_answer
    
    # Сохраняем результат
    user_quiz = UserQuiz(
        user_id=user.id,
        question_id=question.id,
        answer=user_answer,
        is_correct=is_correct,
        answered_at=datetime.now()
    )
    session.add(user_quiz)
    
    if is_correct:
        user.diamonds += question.reward
        session.commit()
        
        await callback.message.edit_text(
            "✅ Правильный ответ!\n\n"
            f"Вы получили {question.reward} 💎\n"
            f"Ваш баланс: {user.diamonds} 💎"
        )
    else:
        session.commit()
        
        await callback.message.edit_text(
            "❌ Неправильный ответ!\n\n"
            f"Правильный ответ: {question.correct_answer}"
        )
    
    await state.clear()
    
    # Предлагаем следующий вопрос
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Следующий вопрос", callback_data="quiz")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
    ])
    
    await callback.message.answer(
        "Хотите ответить на следующий вопрос?",
        reply_markup=keyboard
    )

# Обработчик добавления вопроса
@router.callback_query(F.data == "add_question")
async def add_question(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.waiting_for_question)
    await callback.message.edit_text(
        "📝 Добавление вопроса\n\n"
        "Введите текст вопроса:"
    )

# Обработчик получения текста вопроса
@router.message(QuizStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await state.set_state(QuizStates.waiting_for_options)
    await message.answer(
        "Теперь введите варианты ответа через запятую:"
    )

# Обработчик получения вариантов ответа
@router.message(QuizStates.waiting_for_options)
async def process_options(message: Message, state: FSMContext):
    options = [opt.strip() for opt in message.text.split(",")]
    if len(options) < 2:
        await message.answer(
            "❌ Должно быть как минимум 2 варианта ответа. Попробуйте еще раз:"
        )
        return
    
    await state.update_data(options=options)
    await state.set_state(QuizStates.waiting_for_correct_answer)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for i, option in enumerate(options):
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=option,
                callback_data=f"correct_{i}"
            )
        ])
    
    await message.answer(
        "Выберите правильный ответ:",
        reply_markup=keyboard
    )

# Обработчик выбора правильного ответа
@router.callback_query(F.data.startswith("correct_"))
async def process_correct_answer(callback: CallbackQuery, state: FSMContext):
    answer_index = int(callback.data.split("_")[1])
    data = await state.get_data()
    options = data['options']
    correct_answer = options[answer_index]
    
    await state.update_data(correct_answer=correct_answer)
    await state.set_state(QuizStates.waiting_for_reward)
    
    await callback.message.edit_text(
        "Теперь введите награду за правильный ответ в алмазах:"
    )

# Обработчик получения награды
@router.message(QuizStates.waiting_for_reward)
async def process_reward(message: Message, state: FSMContext):
    try:
        reward = int(message.text)
        if reward <= 0:
            raise ValueError
        
        data = await state.get_data()
        session = get_session()
        
        question = QuizQuestion(
            question=data['question'],
            options=json.dumps(data['options']),
            correct_answer=data['correct_answer'],
            reward=reward,
            created_at=datetime.now()
        )
        session.add(question)
        session.commit()
        
        await state.clear()
        await message.answer(
            "✅ Вопрос успешно добавлен!\n\n"
            f"Вопрос: {data['question']}\n"
            f"Варианты ответа: {', '.join(data['options'])}\n"
            f"Правильный ответ: {data['correct_answer']}\n"
            f"Награда: {reward} 💎"
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат награды. Пожалуйста, введите положительное число:"
        ) 