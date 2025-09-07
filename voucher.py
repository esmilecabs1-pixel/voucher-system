from flask import Flask, render_template, request, jsonify
import routeros_api
import random
import string
import os

app = Flask(__name__)

# MikroTik connection configuration
MIKROTIK_HOST = os.getenv("MIKROTIK_HOST", "192.168.88.1")
MIKROTIK_USER = os.getenv("MIKROTIK_USER", "admin")
MIKROTIK_PASS = os.getenv("MIKROTIK_PASS", "")

def generate_voucher(length=8):
    """Generate a random alphanumeric voucher code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_user_to_mikrotik(username):
    """Add user to MikroTik Hotspot. Returns True if successful."""
    try:
        connection = routeros_api.RouterOsApiPool(
            MIKROTIK_HOST,
            username=MIKROTIK_USER,
            password=MIKROTIK_PASS,
            plaintext_login=True
        )
        api = connection.get_api()
        api.get_resource('/ip/hotspot/user').add(name=username, password=username, profile='default')
        connection.disconnect()
        return True
    except Exception as e:
        print(f"Failed to add user {username} to MikroTik: {e}")
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/generate", methods=["POST"])
def generate():
    voucher = generate_voucher()
    if add_user_to_mikrotik(voucher):
        return jsonify({"status": "success", "voucher": voucher})
    else:
        return jsonify({"status": "error", "message": "MikroTik unreachable"})

if __name__ == "__main__":
    app.run(debug=True)
