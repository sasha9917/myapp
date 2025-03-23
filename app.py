from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)  # ← Це має бути ДО @app.route

# Підключення до бази
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM messages;')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', messages=messages)

@app.route('/add', methods=['POST'])
def add():
    content = request.form['content']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO messages (content) VALUES (%s)', (content,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

# Запуск сервера
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)