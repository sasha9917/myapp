import psycopg2
import os

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            sslmode='require'
        )
        return conn
    except psycopg2.Error as e:
        print("Помилка зʼєднання з базою:", e)
        return None