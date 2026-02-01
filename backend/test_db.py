import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

print("Connecting to:", DATABASE_URL)
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("SELECT current_database(), current_user, inet_server_addr();")
print("Connected! →", cur.fetchall())

cur.execute("SELECT * FROM users;")
rows = cur.fetchall()
print("Existing users:", rows)

conn.close()