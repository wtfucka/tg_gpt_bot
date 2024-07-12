import os

from dotenv import load_dotenv
# Загрузка переменных окружения
load_dotenv()

# Константы
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PROXYAI_TOKEN = os.getenv('PROXYAI_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
