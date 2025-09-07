from flask import Flask, render_template, request, flash
import random
import string
import sqlite3
import os
from functools import wraps
from routeros_api import RouterOsApiPool

app = Flask(__name__, template_folder='.', static_folder='.')
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

DB_FILE = 'vouchers.db'
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ---------------------- Database Setup ----------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS vouchers (
            username TEXT PRIMARY KEY,
            code TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------------- Helper Functions ----------------------
def generate_voucher(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_all_vouchers():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT username, code FROM vouchers')
    data = c.fetchall()
    conn.close()
    return dict(data)

def get_voucher(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT code FROM vouchers WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def save_voucher(username, code):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO vouchers(username, code) VALUES (?, ?)', (username, code))
    conn.commit()
    conn.close()

# ---------------------- Mikrotik Integration ----------------------
def add_to_mikrotik(username, password):
    try:
        api_pool = RouterOsApiPool(
            host=os.getenv("MT_HOST", "172.17.0.1"),
            username=os.getenv("MT_USER", "cabigas"),
            password=os.getenv("MT_PASS", "Esmilefb@Genuin3"),
            port=int(os.getenv("MT_PORT", 8728)),
            plaintext_login=True
        )
        api = api_pool.get_api()

        api.get_resource('/ip/hotspot/user').add(
            name=username,
            password=password,
            profile=os.getenv("MT_PROFILE", "default")
        )

        api_pool.disconnect()
        return True
    except Exception as e:
        print("Mikrotik error:", e)
        return False

# ---------------------- Routes ----------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    username = ""
    voucher_code = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            existing = get_voucher(username)
            if existing:
                voucher_code = existing
                flash('Voucher already exists for this username!', 'info')
            else:
                voucher_code = generate_voucher()
                save_voucher(username, voucher_code)

                # Add to Mikrotik
                if add_to_mikrotik(username, voucher_code):
                    flash('Voucher generated and added to Mikrotik!', 'success')
                else:
                    flash('Voucher saved but Mikrotik connection failed!', 'error')

    return render_template('index.html', username=username, voucher=voucher_code)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        password = request.args.get('password', '')
        if password != ADMIN_PASSWORD:
            return "Unauthorized! Add ?password=YOUR_PASSWORD in URL.", 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin():
    vouchers = get_all_vouchers()
    return render_template('admin.html', vouchers=vouchers)

if __name__ == '__main__':
    app.run(debug=True)
