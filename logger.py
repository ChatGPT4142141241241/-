import logging
import logging.handlers
import os
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logger(name: str) -> logging.Logger:
    """
    Настройка логгера для модуля
    
    Args:
        name: Имя модуля
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем директорию для логов, если она не существует
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Создаем форматтер
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Добавляем обработчик для вывода в файл
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Добавляем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Создаем логгер для всего приложения
logger = setup_logger('ml_helper_bot')

def log_error(error: Exception, context: str = "") -> None:
    """
    Логирование ошибок с контекстом
    
    Args:
        error: Объект исключения
        context: Контекст, в котором произошла ошибка
    """
    error_message = f"Ошибка в {context}: {str(error)}"
    logger.error(error_message, exc_info=True)

def log_info(message: str, context: str = "") -> None:
    """
    Логирование информационных сообщений
    
    Args:
        message: Текст сообщения
        context: Контекст сообщения
    """
    if context:
        message = f"[{context}] {message}"
    logger.info(message)

def log_warning(message: str, context: str = "") -> None:
    """
    Логирование предупреждений
    
    Args:
        message: Текст сообщения
        context: Контекст сообщения
    """
    if context:
        message = f"[{context}] {message}"
    logger.warning(message)

def log_debug(message: str, context: str = "") -> None:
    """
    Логирование отладочных сообщений
    
    Args:
        message: Текст сообщения
        context: Контекст сообщения
    """
    if context:
        message = f"[{context}] {message}"
    logger.debug(message) 