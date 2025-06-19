import sqlite3
from datetime import datetime, timedelta

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            marketplace TEXT,
            tariff TEXT DEFAULT 'free',
            requests_left INTEGER DEFAULT 3,
            subscription_until TEXT DEFAULT 'none'
        )
    ''')
    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "marketplace": row[1],
            "tariff": row[2],
            "requests_left": row[3],
            "subscription_until": row[4],
        }
    return None


def create_user(user_id: int, marketplace: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO users (user_id, marketplace, tariff, requests_left, subscription_until)
        VALUES (?, ?, 'free', 3, 'none')
    ''', (user_id, marketplace))
    conn.commit()
    conn.close()


def update_marketplace(user_id: int, marketplace: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET marketplace = ? WHERE user_id = ?", (marketplace, user_id))
    conn.commit()
    conn.close()


def decrement_requests(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT requests_left FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row and row[0] > 0:
        new_val = row[0] - 1
        c.execute("UPDATE users SET requests_left = ? WHERE user_id = ?", (new_val, user_id))
    conn.commit()
    conn.close()


def reset_requests(user_id: int, amount: int = 3):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET requests_left = ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()


def upgrade_to_premium(user_id: int, days: int = 30):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    until = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    c.execute('''
        UPDATE users
        SET tariff = 'premium',
            subscription_until = ?,
            requests_left = 9999
        WHERE user_id = ?
    ''', (until, user_id))
    conn.commit()
    conn.close()