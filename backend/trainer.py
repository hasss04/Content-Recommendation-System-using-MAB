import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql:// "
)

def train_models():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, genre, content_id,
               SUM(reward) AS successes,
               COUNT(*) - SUM(reward) AS failures
        FROM interactions
        GROUP BY user_id, genre, content_id
    """)
    data = cur.fetchall()

    for user_id, genre, content_id, succ, fail in data:
        alpha = succ + 1
        beta = fail + 1
        cur.execute("""
            INSERT INTO user_models (user_id, genre, content_id, alpha, beta, last_trained)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, genre, content_id)
            DO UPDATE SET alpha=%s, beta=%s, last_trained=%s
        """, (
            user_id, genre, content_id, alpha, beta, datetime.now(),
            alpha, beta, datetime.now()
        ))

    conn.commit()
    conn.close()
    print("RL model updated dynamically.")

if __name__ == "__main__":
    train_models()