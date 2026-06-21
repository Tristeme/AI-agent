import sqlite3
from datetime import datetime

# Local SQLite database path
DB_PATH = "storage/app.db"


def init_db():
    """
    Initialise SQLite database.

    Creates the chat_logs table if it does not already exist.
    This table is used for traceability and basic audit logging.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Store each user message and AI response with timestamp
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
    """
    Save one chat interaction to SQLite.

    This supports traceability by keeping a record of:
    - user prompt
    - AI response
    - timestamp
    """
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