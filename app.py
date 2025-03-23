from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

from db import get_db_connection  # перенесено в окремий файл

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-dev-key')

# Головна сторінка
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    if conn is None:
        return 'Помилка зʼєднання з базою'

    cur = conn.cursor()
    cur.execute('SELECT * FROM messages ORDER BY id ASC;')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', messages=messages)

# Додавання повідомлення
@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/login')

    content = request.form['content']
    if not content.strip():
        return redirect('/')

    username = session.get('username')

    conn = get_db_connection()
    if conn is None:
        return 'Помилка зʼєднання з базою'

    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO messages (content, username) VALUES (%s, %s)', (content, username))
        conn.commit()
        print(f"[LOG] {username} надіслав повідомлення: {content}")
    except Exception as e:
        print("Помилка при вставці повідомлення:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return redirect('/')

# JSON API для автоматичного оновлення
@app.route('/messages')
def get_messages():
    conn = get_db_connection()
    if conn is None:
        return jsonify([])

    cur = conn.cursor()
    cur.execute('SELECT * FROM messages ORDER BY id ASC;')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(messages)

# Реєстрація
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        if conn is None:
            return 'Помилка зʼєднання з базою'

        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            conn.commit()
            print(f"[LOG] Зареєстровано нового користувача: {username}")
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return 'Користувач з таким іменем вже існує'
        finally:
            cur.close()
            conn.close()
        return redirect('/login')

    return render_template('register.html')

# Вхід
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn is None:
            return 'Помилка зʼєднання з базою'

        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            print(f"[LOG] Користувач {username} увійшов у систему")
            return redirect('/')
        else:
            return 'Невірне імʼя користувача або пароль'

    return render_template('login.html')

# Вихід
@app.route('/logout')
def logout():
    user = session.get('username', 'невідомий')
    session.clear()
    print(f"[LOG] Користувач {user} вийшов із системи")
    return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)