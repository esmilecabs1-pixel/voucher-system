from flask import Flask, render_template, request, jsonify
import routeros_api
import random
import string
import os

app = Flask(__name__)

# MikroTik connection settings (set in Render environment)
MIKROTIK_HOST = os.environ.get("MIKROTIK_HOST", "192.168.88.1")
MIKROTIK_USER = os.environ.get("MIKROTIK_USER", "admin")
MIKROTIK_PASSWORD = os.environ.get("MIKROTIK_PASSWORD", "")
MIKROTIK_PORT = int(os.environ.get("MIKROTIK_PORT", 8728))

def generate_voucher_code(length=8):
    """Generate a random alphanumeric voucher code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_voucher_to_mikrotik(username, password):
    """Connect to MikroTik and add the voucher as a hotspot user."""
    try:
        connection = routeros_api.RouterOsApiPool(
            MIKROTIK_HOST,
            username=MIKROTIK_USER,
            password=MIKROTIK_PASSWORD,
            port=MIKROTIK_PORT,
            plaintext_login=True
        )
        api = connection.get_api()
        api.get_resource('/ip/hotspot/user').add(name=username, password=password, profile='default')
        connection.disconnect()
        return True, "Voucher added successfully"
    except Exception as e:
        return False, str(e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/generate", methods=["POST"])
def generate():
    username = generate_voucher_code()
    password = generate_voucher_code()
    
    success, message = add_voucher_to_mikrotik(username, password)
    
    if success:
        return jsonify({"status": "success", "username": username, "password": password})
    else:
        return jsonify({"status": "error", "message": f"Failed to add to MikroTik: {message}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
