import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ml_helper.db")

# Настройки администраторов
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

# Настройки магазина
SHOP_CATEGORIES = [
    "Скины",
    "Эмодзи",
    "Рамки",
    "Анимации",
    "Другое"
]

# Настройки викторины
QUIZ_REWARD_RANGE = (10, 50)  # Диапазон наград за правильный ответ
QUIZ_MAX_ATTEMPTS = 3  # Максимальное количество попыток на вопрос

# Настройки турниров
TOURNAMENT_MIN_TEAM_SIZE = 1
TOURNAMENT_MAX_TEAM_SIZE = 5

# Настройки профиля
DEFAULT_DIAMONDS = 100  # Количество алмазов при создании профиля
DEFAULT_EXPERIENCE = 0  # Опыт при создании профиля

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "bot.log"

# Настройки кэширования
CACHE_TTL = 300  # Время жизни кэша в секундах

# Настройки безопасности
MAX_MESSAGE_LENGTH = 4096  # Максимальная длина сообщения
MAX_BUTTONS_PER_ROW = 3  # Максимальное количество кнопок в ряду
MAX_BUTTONS_TOTAL = 100  # Максимальное общее количество кнопок

# Настройки локализации
DEFAULT_LANGUAGE = "ru"
SUPPORTED_LANGUAGES = ["ru", "en"]

# Настройки API
API_TIMEOUT = 30  # Таймаут для API запросов в секундах
API_RETRY_COUNT = 3  # Количество попыток при ошибке API

# Настройки уведомлений
NOTIFICATION_DELAY = 5  # Задержка между уведомлениями в секундах
MAX_NOTIFICATIONS_PER_DAY = 10  # Максимальное количество уведомлений в день

# Пути к файлам данных
DATA_DIR = 'data'
HEROES_FILE = os.path.join(DATA_DIR, 'heroes.txt')
ITEMS_FILE = os.path.join(DATA_DIR, 'items.txt')
GUIDES_FILE = os.path.join(DATA_DIR, 'guides.txt')
TERMS_FILE = os.path.join(DATA_DIR, 'terms.txt')
QUIZ_FILE = os.path.join(DATA_DIR, 'quiz.txt')
USER_PROFILES_FILE = os.path.join(DATA_DIR, 'user_profiles.txt')

# Путь к изображениям
IMAGES_DIR = 'images'
HEROES_IMAGES_DIR = os.path.join(IMAGES_DIR, 'heroes')

# Создание директорий, если они не существуют
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(HEROES_IMAGES_DIR, exist_ok=True) 