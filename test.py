import psycopg2
conn = psycopg2.connect("postgresql://")
cur = conn.cursor()
cur.execute("SELECT version()")
print(cur.fetchone())
conn.close()
