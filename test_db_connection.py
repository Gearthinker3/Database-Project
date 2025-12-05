import psycopg2

try:
    conn = psycopg2.connect(
        host="ada.mines.edu",
        database="csci403",
        user="loganmatthews",   # e.g., jsmith
        password="#Logmatt0826",
        port="5432"
    )
    
    print("Connected successfully!")

    # optional test query
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("PostgreSQL version:", cur.fetchone())

    conn.close()

except Exception as e:
    print("Connection failed:", e)
