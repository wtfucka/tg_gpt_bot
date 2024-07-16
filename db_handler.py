import sqlite3
from datetime import datetime, timedelta, timezone

from logger_config import setup_logging

logger = setup_logging()


class DatabaseHandler:
    def __init__(self):
        self.conn = sqlite3.connect('tg_bot.db')
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_date INTEGER,
                    user_id INTEGER,
                    role TEXT,
                    content TEXT
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS whitelist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    date_add INTEGER,
                    date_off INTEGER,
                    active BOOLEAN
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    tokens_used INTEGER
                )
            ''')

    def add_user_to_whitelist(self, user_id: int, username: str) -> None:
        with self.conn:
            date_add = int(datetime.now(
                tz=timezone(
                    timedelta(
                        hours=3
                        )
                    )
                ).timestamp())
            self.conn.execute('''
                INSERT INTO whitelist (
                                    user_id,
                                    username,
                                    date_add,
                                    active)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, date_add, True))

    def deactivate_user_in_whitelist(self, user_id: int) -> None:
        with self.conn:
            date_off = int(datetime.now(
                tz=timezone(
                    timedelta(
                        hours=3
                        )
                    )
                ).timestamp())
            self.conn.execute('''
                UPDATE whitelist SET active = ?, date_off = ? WHERE user_id = ?
            ''', (False, date_off, user_id))

    def activate_user_in_whitelist(self, user_id: int) -> None:
        with self.conn:
            self.conn.execute('''
                UPDATE whitelist SET active = ?, date_off = ? WHERE user_id = ?
            ''', (True, None, user_id))

    def save_message(self, user_id: int, role: str, content: str) -> None:
        with self.conn:
            message_date = int(datetime.now().timestamp())
            self.conn.execute('''
                INSERT INTO history (
                              message_date,
                              user_id,
                              role,
                              content)
                VALUES (?, ?, ?, ?)
            ''', (message_date, user_id, role, content))

    def get_history(self, user_id: int) -> list:
        cursor = self.conn.execute(
            """
            SELECT
                    role,
                    content,
                    message_date
            FROM history
            WHERE user_id = ?
                and role = 'user'
            ORDER BY message_date desc
            LIMIT 3
            """,
            (user_id,))
        return [
            {'role': row[0],
             'content': row[1],
             'message_date': row[2]
             } for row in cursor.fetchall()
            ]

    def log_tokens(self, user_id: int, tokens: int) -> None:
        with self.conn:
            self.conn.execute('''
                INSERT INTO tokens (user_id, tokens_used) VALUES (?, ?)
            ''', (user_id, tokens))

    def get_whitelist(self):
        cursor = self.conn.execute(
            'SELECT user_id, username FROM whitelist WHERE active = 1'
            )
        return [
            {'user_id': row[0],
             'username': row[1]} for row in cursor.fetchall()
            ]

    def get_token_usage(self):
        cursor = self.conn.execute(
            'SELECT user_id, SUM(tokens_used) FROM tokens GROUP BY user_id'
            )
        return [
            {'user_id': row[0],
             'tokens_used': row[1]} for row in cursor.fetchall()
             ]

    def is_user_whitelisted(self, user_id: int) -> bool:
        cursor = self.conn.execute(
            'SELECT active FROM whitelist WHERE user_id = ? AND active = 1',
            (user_id,)
            )
        return cursor.fetchone() is not None
