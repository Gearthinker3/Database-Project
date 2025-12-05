import psycopg2

def test_connection(username, password):
    connection = psycopg2.connect(
        host="ada.mines.edu",
        database="csci403",
        user=username,
        password=password,
        port=5432
    )
    return connection


def get_connection(username, password):
    return psycopg2.connect(
        host="ada.mines.edu",
        database="csci403",
        user=username,
        password=password,
        port=5432
    )
