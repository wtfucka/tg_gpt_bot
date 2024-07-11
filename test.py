import sqlite3
from datetime import datetime, timedelta, timezone

conn = sqlite3.connect('tg_bot.db')

with conn:
    date_add = int(datetime.now(
        tz=timezone(
            timedelta(
                hours=3
                )
            )
        ).timestamp())
    conn.execute('''
        INSERT INTO whitelist (
                            user_id,
                            username,
                            date_add,
                            active)
        VALUES (?, ?, ?, ?)
    ''', (378606353, 'lrazanova', date_add, True))
