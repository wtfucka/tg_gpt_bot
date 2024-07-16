from datetime import datetime, timedelta

from telegram import (InlineKeyboardButton,
                      InlineKeyboardMarkup,
                      MessageEntity,
                      Update
                      )
from telegram.ext import ContextTypes

import db_handler
import openai_handler
from gpt_instructions import answer_instructions, user_instructions
from logger_config import setup_logging
from proxyai_balance import check_current_balance

logger = setup_logging()


class UserHandler:
    def __init__(self,
                 db_handler: db_handler.DatabaseHandler,
                 openai_handler: openai_handler.OpenAIHandler,
                 admin_chat_id: int
                 ):
        self.db_handler = db_handler
        self.openai_handler = openai_handler
        self.admin_chat_id = admin_chat_id
        self.selected_model = 'gpt-4o'

    def get_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton('GPT-3.5-Turbo',
                                  callback_data='gpt-3.5-turbo-0613'),
             InlineKeyboardButton('GPT-4-Turbo',
                                  callback_data='gpt-4-turbo'),
             InlineKeyboardButton('GPT-4o',
                                  callback_data='gpt-4o')],
        ]
        return InlineKeyboardMarkup(keyboard)

    async def start(self,
                    update: Update,
                    context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id

        if user_id == self.admin_chat_id:
            reply_markup = self.get_admin_keyboard()
        else:
            reply_markup = self.get_keyboard()

        await update.message.reply_text(
            'Привет! Это чат-бот с интегрированной языковой моделью OpenAI.'
            '\nВыбери модель:',
            reply_markup=reply_markup
                )

    def get_admin_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton('GPT-3.5-Turbo',
                                  callback_data='gpt-3.5-turbo-0613'),
             InlineKeyboardButton('GPT-4-Turbo',
                                  callback_data='gpt-4-turbo'),
             InlineKeyboardButton('GPT-4o',
                                  callback_data='gpt-4o')],
            [InlineKeyboardButton('Добавить доступ',
                                  callback_data='add_user')],
            [InlineKeyboardButton('Открыть доступ',
                                  callback_data='activate_user'),
             InlineKeyboardButton('Закрыть доступ',
                                  callback_data='deactivate_user')],
            [InlineKeyboardButton('Список пользователей',
                                  callback_data='check_users'),
             InlineKeyboardButton('Запрос баланса',
                                  callback_data='check_balance')]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def handle_message(self,
                             update: Update,
                             context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        user_message = update.message.text
        previous_day = int((datetime.now() - timedelta(days=1)).timestamp())

        if not self.db_handler.is_user_whitelisted(user_id):
            await update.message.reply_text('У вас нет доступа к этому боту.')
            return

        # Временное решение
        if self.selected_model == 'add_user':
            return self.db_handler.add_user_to_whitelist(
                    user_message.split()[0],
                    user_message.split()[1]
                )
        elif self.selected_model == 'deactivate_user':
            return self.db_handler.deactivate_user_in_whitelist(
                    user_message.split()[0]
                )
        elif self.selected_model == 'activate_user':
            return self.db_handler.activate_user_in_whitelist(
                    user_message.split()[0]
                )

        self.db_handler.save_message(user_id, 'user', user_message)

        instructions = '\n'.join([user_instructions, answer_instructions])
        system_message = {'role': 'system',
                          'content': instructions}
        history = self.db_handler.get_history(user_id)
        history_messages = [
            {'role': entry['role'],
             'content': entry['content']
             } for entry in history if entry['message_date'] > previous_day
             ]
        messages = [system_message] + history_messages

        response, tokens_used = await self.openai_handler.get_response(
            self.selected_model,
            messages
            )

        self.db_handler.save_message(user_id, 'assistant', response)
        self.db_handler.log_tokens(user_id, tokens_used)

        await update.message.reply_text(response, parse_mode='Markdown')

    async def button(self,
                     update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        self.selected_model = query.data

        if query.data == 'check_users':
            users = self.db_handler.get_whitelist()
            token_usage = self.db_handler.get_token_usage()
            user_info = '\n'.join(
                [f"ID: {user['user_id']}, Username: {user['username']}" for user in users]
                )
            token_info = '\n'.join(
                [f"ID: {token['user_id']}, Tokens used: {token['tokens_used']}" for token in token_usage]
                )
            await query.edit_message_text(
                f'Пользователи:\n{user_info}\n\nИспользование токенов:\n{token_info}'
                )
        # Асинхронный запрос баланса
        elif query.data == 'check_balance':
            balance = check_current_balance()
            await query.edit_message_text(f'Текущий баланс: {balance} рублей.')
        else:
            await query.edit_message_text(
                f'Выбрана модель: {self.selected_model}'
                )

    # async def format_code_blocks(self, text: str) -> list:
    #     entities = []
    #     start = 0
    #     while start < len(text):
    #         start = text.find('```', start)
    #         if start == -1:
    #             break
    #         end = text.find('```', start + 3)
    #         if end == -1:
    #             break
    #         entities.append(MessageEntity(type=MessageEntity.CODE,
    #                                       offset=start,
    #                                       length=end - start + 3))
    #         start = end + 3
    #     return entities
