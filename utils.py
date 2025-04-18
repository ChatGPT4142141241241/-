import re
from typing import List, Optional, Union
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    MAX_MESSAGE_LENGTH,
    MAX_BUTTONS_PER_ROW,
    MAX_BUTTONS_TOTAL,
    DEFAULT_LANGUAGE
)

def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> List[str]:
    """
    Разделяет длинное сообщение на части
    
    Args:
        text: Текст сообщения
        max_length: Максимальная длина части
        
    Returns:
        List[str]: Список частей сообщения
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    for word in text.split():
        if len(current_part) + len(word) + 1 <= max_length:
            current_part += f"{word} "
        else:
            parts.append(current_part.strip())
            current_part = f"{word} "
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts

def create_keyboard(
    buttons: List[Union[str, tuple]],
    row_width: int = MAX_BUTTONS_PER_ROW
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру из списка кнопок
    
    Args:
        buttons: Список кнопок или пар (текст, callback_data)
        row_width: Количество кнопок в ряду
        
    Returns:
        InlineKeyboardMarkup: Объект клавиатуры
    """
    keyboard = []
    current_row = []
    
    for button in buttons:
        if isinstance(button, tuple):
            text, callback_data = button
        else:
            text = callback_data = button
        
        if len(current_row) < row_width:
            current_row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        else:
            keyboard.append(current_row)
            current_row = [InlineKeyboardButton(text=text, callback_data=callback_data)]
    
    if current_row:
        keyboard.append(current_row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def format_date(date: datetime) -> str:
    """
    Форматирует дату в строку
    
    Args:
        date: Объект даты
        
    Returns:
        str: Отформатированная дата
    """
    return date.strftime("%d.%m.%Y %H:%M")

def format_number(number: Union[int, float]) -> str:
    """
    Форматирует число в строку с разделителями
    
    Args:
        number: Число для форматирования
        
    Returns:
        str: Отформатированное число
    """
    return f"{number:,}".replace(",", " ")

def validate_username(username: str) -> bool:
    """
    Проверяет валидность имени пользователя
    
    Args:
        username: Имя пользователя
        
    Returns:
        bool: True если имя валидно, иначе False
    """
    pattern = r"^[a-zA-Z0-9_]{3,32}$"
    return bool(re.match(pattern, username))

def validate_email(email: str) -> bool:
    """
    Проверяет валидность email
    
    Args:
        email: Email адрес
        
    Returns:
        bool: True если email валиден, иначе False
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def get_language_code(language: str) -> str:
    """
    Возвращает код языка
    
    Args:
        language: Название языка
        
    Returns:
        str: Код языка
    """
    language_codes = {
        "русский": "ru",
        "english": "en",
        "russian": "ru"
    }
    return language_codes.get(language.lower(), DEFAULT_LANGUAGE)

def calculate_level(experience: int) -> int:
    """
    Вычисляет уровень на основе опыта
    
    Args:
        experience: Количество опыта
        
    Returns:
        int: Уровень
    """
    level = 1
    exp_needed = 100
    
    while experience >= exp_needed:
        experience -= exp_needed
        level += 1
        exp_needed = int(exp_needed * 1.5)
    
    return level

def calculate_experience_needed(level: int) -> int:
    """
    Вычисляет необходимое количество опыта для следующего уровня
    
    Args:
        level: Текущий уровень
        
    Returns:
        int: Необходимое количество опыта
    """
    exp_needed = 100
    for _ in range(1, level):
        exp_needed = int(exp_needed * 1.5)
    return exp_needed

def format_time(seconds: int) -> str:
    """
    Форматирует время в секундах в строку
    
    Args:
        seconds: Количество секунд
        
    Returns:
        str: Отформатированное время
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def sanitize_text(text: str) -> str:
    """
    Очищает текст от HTML-тегов и специальных символов
    
    Args:
        text: Текст для очистки
        
    Returns:
        str: Очищенный текст
    """
    # Удаляем HTML-теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Экранируем специальные символы
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    return text 