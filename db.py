import psycopg2
import psycopg2.extras

def get_connection():
    return psycopg2.connect(
        host="ada.mines.edu",
        database="csci403",
        user="",
        password="",
        port=5432
    )
