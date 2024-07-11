import time
from datetime import datetime

import requests
import schedule
import telegram

from logger_config import setup_logging
from main import ADMIN_CHAT_ID, PROXYAI_TOKEN, TELEGRAM_TOKEN

logger = setup_logging()

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def get_balance(api_key):
    url = "https://api.proxyapi.ru/proxyapi/balance"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 402:
            return 'Недостаточно средств для выполнения запроса.'

        data = response.json()
        return data["balance"]
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе баланса: {e}")
        return None


def notify_admin(admin_chat_id, balance):
    message = f"Баланс достиг {balance} рублей."
    try:
        # Используем метод отправки сообщения Telegram бота
        bot.send_message(chat_id=admin_chat_id, text=message)
    except telegram.error as e:
        logger.error(f"Ошибка при отправке уведомления администратору: {e}")


def check_balance():
    current_hour = datetime.now().hour
    if 8 <= current_hour < 22:
        balance = get_balance(PROXYAI_TOKEN)
        if balance is not None and balance < 50:
            notify_admin(ADMIN_CHAT_ID, balance)


# Запускаем проверку каждые 3 часа
schedule.every(3).hours.do(check_balance)


# Запуск планировщика в отдельном потоке
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
