# ML Helper AI - Telegram Bot

Telegram-бот для помощи игрокам Mobile Legends.

## Функциональность

- 🃏 Карточки героев с гайдами
- 🧠 Тир-лист 2025
- 📘 Словарь терминов и сленга
- 🎭 Легенды ML (фан-контент)
- 👤 Профиль игрока
- ☀️ Ежедневные советы
- 🎮 Викторина
- 🛍 Магазин (черный рынок)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ml_helper_bot.git
cd ml_helper_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и заполните его:
```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
```

4. Создайте необходимые директории:
```bash
mkdir data images images/heroes
```

## Запуск

```bash
python bot.py
```

## Структура проекта

- `bot.py` - основной файл бота
- `config.py` - конфигурация
- `data/` - файлы с данными
- `images/` - изображения
- `requirements.txt` - зависимости

## Админ-команды

- `/add_hero` - Добавить героя
- `/update_guide` - Обновить гайд
- `/delete_hero` - Удалить героя
- `/add_term` - Добавить термин
- `/add_quiz` - Добавить вопрос
- `/ban_user` - Забанить пользователя
- `/stats` - Статистика 