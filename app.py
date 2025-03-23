from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'sasha-super-secret-key-123'

# Підключення до бази

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        sslmode='require'
    )
    return conn

# Головна сторінка
@app.route('/')
def index():
    conn = get_db_connection()
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
    username = session.get('username')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO messages (content, username) VALUES (%s, %s)', (content, username))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

# JSON API для автоматичного оновлення
@app.route('/messages')
def messages():
    conn = get_db_connection()
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
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            conn.commit()
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
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/')
        else:
            return 'Невірне імʼя користувача або пароль'

    return render_template('login.html')

# Вихід
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)