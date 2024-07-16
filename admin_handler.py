from telegram import Update
from telegram.ext import ContextTypes

import db_handler
from logger_config import setup_logging

logger = setup_logging()


class AdminHandler:
    def __init__(self,
                 db_handler: db_handler.DatabaseHandler,
                 admin_chat_id: int):
        self.db_handler = db_handler
        self.admin_chat_id = admin_chat_id
        self.idx_message_error = (
            'Ошибка: необходимо указать username и user_id.'
            )
        self.value_message_error = (
            'Ошибка: user_id должен быть целым числом.'
        )
        self.permission_message = 'У вас нет прав для выполнения этой команды.'

    async def add_user_command(self,
                               update: Update,
                               context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id

        if str(user_id) != str(self.admin_chat_id):
            await update.message.reply_text(self.permission_message)
            return
        try:
            username = context.args[0]
            target_user_id = int(context.args[1])
            self.db_handler.add_user_to_whitelist(target_user_id, username)
            await update.message.reply_text(
                f'Пользователь {username} добавлен в whitelist.'
                )
        except IndexError:
            await update.message.reply_text(self.idx_message_error)
        except ValueError:
            await update.message.reply_text(self.value_message_error)
        except Exception as e:
            logger.error(f'Ошибка: {e}')
            await update.message.reply_text(
                'Произошла ошибка при добавлении пользователя.'
                )

    async def deactivate_user_command(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
            ) -> None:
        user_id = update.message.from_user.id

        if user_id != self.admin_chat_id:
            await update.message.reply_text(self.permission_message)
            return

        try:
            target_user_id = int(context.args[0])
            self.db_handler.deactivate_user_in_whitelist(target_user_id)
            await update.message.reply_text(
                f'Пользователь с ID {target_user_id} деактивирован.'
                )
        except IndexError:
            await update.message.reply_text(self.idx_message_error)
        except ValueError:
            await update.message.reply_text(self.value_message_error)
        except Exception as e:
            logger.error(f'Error in deactivate_user_command: {e}')
            await update.message.reply_text(
                'Произошла ошибка при деактивации пользователя.'
                )

    async def activate_user_command(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
            ) -> None:
        user_id = update.message.from_user.id

        if user_id != self.admin_chat_id:
            await update.message.reply_text(self.permission_message)
            return

        try:
            target_user_id = int(context.args[0])
            self.db_handler.activate_user_in_whitelist(target_user_id)
            await update.message.reply_text(
                f'Пользователь с ID {target_user_id} активирован.'
                )
        except IndexError:
            await update.message.reply_text(self.idx_message_error)
        except ValueError:
            await update.message.reply_text(self.value_message_error)
        except Exception as e:
            logger.error(f'Error in deactivate_user_command: {e}')
            await update.message.reply_text(
                'Произошла ошибка при деактивации пользователя.'
                )

    async def check_users_command(self,
                                  update: Update,
                                  context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        if user_id != self.admin_chat_id:
            await update.message.reply_text(self.permission_message)
            return

        try:
            users = self.db_handler.get_whitelist()
            token_usage = self.db_handler.get_token_usage()
            user_info = "\n".join(
                [f"ID: {user['user_id']}, Username: {user['username']}" for user in users]
                )
            token_info = "\n".join(
                [f"ID: {token['user_id']}, Tokens used: {token['tokens_used']}" for token in token_usage]
                )
            await update.message.reply_text(
                f"Пользователи:\n{user_info}\n\nИспользование токенов:\n{token_info}"
                )
        except Exception as e:
            logger.error(f'Error in check_users_command: {e}')
            await update.message.reply_text(
                'Произошла ошибка при получении списка пользователей.'
                )
