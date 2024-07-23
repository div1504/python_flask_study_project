from flask import Flask, render_template, request, redirect, url_for, current_app
from flask_login import LoginManager, UserMixin, logout_user, login_required
import sqlite3
import secrets
from flask_login import login_user, current_user

app = Flask(__name__)
secret_key = secrets.token_hex()
app.secret_key = secret_key
login_manager = LoginManager()
login_manager.init_app(app)
app.app_context().push()

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Website:
    def __init__(self, id, user_id, name, url):
        self.id = id
        self.user_id = user_id
        self.url = url
        self.name = name

def get_user_by_id(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = {}'.format(int(user_id)))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    else:
        return None
    
# Callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # TODO 1: Implement the user registration.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            error = 'Username already exists.'
            return render_template('register.html', error=error)
        else:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # TODO 2: Implement the user login.
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data and user_data[2] == password:
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # TODO 3: Implement the function for adding websites to user profiles.
    if request.method == 'POST':
        website_name = request.form['website_name']
        website_url = request.form['website_url']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO websites (user_id, name, url) VALUES (?, ?, ?)', (current_user.id, website_name, website_url))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM websites WHERE user_id = ?', (current_user.id,))
    websites = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', websites=websites)

@app.route('/dashboard/<int:website_id>/delete', methods=['POST'])
@login_required
def delete(website_id):
    # TODO 4: Implement the function for deleting websites from user profiles.
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM websites WHERE id = ? AND user_id = ?', (website_id, current_user.id))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

def create_tables():
    # Creates new tables in the database.db database if they do not already exist.
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    with current_app.open_resource("schema.sql") as f:
        c.executescript(f.read().decode("utf8"))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
