import asyncio
import os
from threading import Thread

from dotenv import load_dotenv
from telegram.ext import (Application,
                          CommandHandler,
                          filters,
                          MessageHandler,
                          CallbackQueryHandler
                          )
import schedule

from admin_handler import AdminHandler
from db_handler import DatabaseHandler
from logger_config import setup_logging
from openai_handler import OpenAIHandler
from user_handler import UserHandler

# Настройка логирования
logger = setup_logging()

# Загрузка переменных окружения
load_dotenv()

# Константы
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PROXYAI_TOKEN = os.getenv('PROXYAI_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))


def main():
    # Инициализация бота и обработчиков
    db_handler = DatabaseHandler()
    openai_handler = OpenAIHandler(api_key=PROXYAI_TOKEN)
    user_handler = UserHandler(db_handler, openai_handler, ADMIN_CHAT_ID)
    admin_handler = AdminHandler(db_handler, ADMIN_CHAT_ID)

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler('start',
                                           user_handler.start))
    application.add_handler(CommandHandler('add_user',
                                           admin_handler.add_user_command))
    application.add_handler(CommandHandler(
        'deactivate_user',
        admin_handler.deactivate_user_command)
        )
    application.add_handler(CommandHandler(
        'check_users',
        admin_handler.check_users_command)
        )

    # Регистрация обработчика сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        user_handler.handle_message)
        )

    # Регистрация обработчика нажатий на кнопки
    application.add_handler(CallbackQueryHandler(user_handler.button))

    # Запуск планировщика в отдельном потоке
    scheduler_thread = Thread(target=lambda: schedule.run_continuously())
    scheduler_thread.start()

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
