import sqlite3
from datetime import datetime

DB_PATH = "storage/app.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_chat_log(user_message: str, ai_response: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_logs (user_message, ai_response, created_at)
        VALUES (?, ?, ?)
    """, (
        user_message,
        ai_response,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()