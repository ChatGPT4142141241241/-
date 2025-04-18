from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from database import get_session
from logger import log_error, log_warning
from config import ADMIN_IDS

router = Router()

class BotError(Exception):
    """Базовый класс для ошибок бота"""
    def __init__(self, message: str, user_id: int = None):
        self.message = message
        self.user_id = user_id
        super().__init__(message)

class DatabaseError(BotError):
    """Ошибка работы с базой данных"""
    pass

class ValidationError(BotError):
    """Ошибка валидации данных"""
    pass

class PermissionError(BotError):
    """Ошибка прав доступа"""
    pass

class APIError(BotError):
    """Ошибка API"""
    pass

async def handle_error(event: ErrorEvent) -> None:
    """
    Обработчик всех ошибок бота
    
    Args:
        event: Событие ошибки
    """
    error = event.exception
    context = event.update
    
    # Логируем ошибку
    log_error(error, str(context))
    
    # Если это наша ошибка, отправляем сообщение пользователю
    if isinstance(error, BotError):
        if error.user_id:
            try:
                await context.bot.send_message(
                    error.user_id,
                    f"❌ {error.message}"
                )
            except TelegramAPIError as e:
                log_error(e, "Ошибка отправки сообщения об ошибке")
    
    # Если это ошибка API Telegram, отправляем уведомление администраторам
    elif isinstance(error, TelegramAPIError):
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"⚠️ Ошибка API Telegram:\n{str(error)}"
                )
            except TelegramAPIError as e:
                log_error(e, "Ошибка отправки уведомления администратору")

def handle_database_error(func):
    """
    Декоратор для обработки ошибок базы данных
    
    Args:
        func: Функция, которая может вызвать ошибку базы данных
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            session = get_session()
            session.rollback()
            log_error(e, f"Ошибка базы данных в {func.__name__}")
            raise DatabaseError("Произошла ошибка при работе с базой данных")
    return wrapper

def validate_user_input(func):
    """
    Декоратор для валидации ввода пользователя
    
    Args:
        func: Функция, которая обрабатывает ввод пользователя
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            log_warning(str(e), f"Ошибка валидации в {func.__name__}")
            raise ValidationError(str(e))
    return wrapper

def check_admin(func):
    """
    Декоратор для проверки прав администратора
    
    Args:
        func: Функция, доступная только администраторам
    """
    async def wrapper(*args, **kwargs):
        try:
            # Получаем ID пользователя из аргументов
            user_id = None
            for arg in args:
                if hasattr(arg, 'from_user'):
                    user_id = arg.from_user.id
                    break
            
            if user_id not in ADMIN_IDS:
                raise PermissionError("У вас нет прав для выполнения этой команды", user_id)
            
            return await func(*args, **kwargs)
        except PermissionError:
            raise
        except Exception as e:
            log_error(e, f"Ошибка в функции администратора {func.__name__}")
            raise
    return wrapper

# Регистрируем обработчик ошибок
router.error(handle_error) 