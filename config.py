# config.py
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Данные из my.telegram.org (берутся из переменных окружения)
API_ID = int(os.getenv("36799261", 0))
API_HASH = os.getenv("19e8ed1aeb5696805776d6b0689633cd", "")
BOT_TOKEN = os.getenv("8559397516:AAGDFDiKX9tIG79WwDrhZY48hT9gg7jF8fU", "")

# Аккаунты для отправки жалоб (можно добавить через переменные)
# Формат: PHONE_1=+79001234567, SESSION_1=session1 и т.д.
ACCOUNTS = []
for i in range(1, 11):  # до 10 аккаунтов
    phone = os.getenv(f"PHONE_{i}")
    if phone:
        ACCOUNTS.append({
            "phone": phone,
            "session": f"sessions/session{i}"
        })

# Тексты жалоб
REPORT_TEXTS = [
    "Этот пользователь рассылает порнографию в личные сообщения",
    "Пользователь угрожает расправой и публикует мой адрес",
    "Мошенник, выманивает деньги под видом помощи",
    "Распространяет наркотики, ссылки на запрещённые ресурсы",
    "Оскорбляет по национальному признаку, призывает к насилию",
    "Спам-бот, рассылает рекламу казино",
    "Детская порнография в открытом канале",
    "Кража аккаунтов, фишинговая ссылка",
    "Террористические угрозы, призывы к насилию",
    "Создал фейковый аккаунт от моего имени, клевета"
]

# Настройки задержек
MIN_DELAY = int(os.getenv("MIN_DELAY", 3))
MAX_DELAY = int(os.getenv("MAX_DELAY", 8))
DEFAULT_REPORT_COUNT = int(os.getenv("DEFAULT_REPORT_COUNT", 50))

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
