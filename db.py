import os
import psycopg2
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vip_users (
    user_id BIGINT PRIMARY KEY,
    expired_at TIMESTAMP
)
""")
conn.commit()


def add_vip(user_id, days):
    expired = datetime.utcnow() + timedelta(days=days)

    cursor.execute("""
    INSERT INTO vip_users (user_id, expired_at)
    VALUES (%s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET expired_at = EXCLUDED.expired_at
    """, (user_id, expired))

    conn.commit()


def remove_vip(user_id):
    cursor.execute("DELETE FROM vip_users WHERE user_id=%s", (user_id,))
    conn.commit()


def is_vip(user_id):
    cursor.execute("SELECT expired_at FROM vip_users WHERE user_id=%s", (user_id,))
    result = cursor.fetchone()

    if not result:
        return False

    expired = result[0]

    if datetime.utcnow() > expired:
        remove_vip(user_id)
        return False

    return True


def get_expired_users():
    cursor.execute("SELECT user_id FROM vip_users WHERE expired_at < NOW()")
    return cursor.fetchall()
