import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path("novaos_memory.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            result TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_history(command: str, result: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO history (command, result, timestamp)
        VALUES (?, ?, ?)
    """, (command, result, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_history(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT command, result, timestamp
        FROM history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows