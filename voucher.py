from flask import Flask, render_template, request, jsonify
from routeros_api import RouterOsApiPool
import os
import random
import string

app = Flask(__name__)

# Mikrotik connection settings (update with your router credentials)
ROUTER_HOST = os.getenv("ROUTER_HOST", "192.168.88.1")
ROUTER_USER = os.getenv("ROUTER_USER", "admin")
ROUTER_PASS = os.getenv("ROUTER_PASS", "")
ROUTER_PORT = int(os.getenv("ROUTER_PORT", 8728))

vouchers = []  # In-memory store; replace with database if needed

def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_hotspot_user(username, code):
    try:
        connection = RouterOsApiPool(
            host=ROUTER_HOST,
            username=ROUTER_USER,
            password=ROUTER_PASS,
            port=ROUTER_PORT,
            plaintext_login=True
        )
        api = connection.get_api()
        api.get_resource('/ip/hotspot/user').add(
            name=username,
            password=code,
            profile="default"
        )
        connection.disconnect()
        return True
    except Exception as e:
        print("Router connection error:", e)
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    username = request.form.get("username")
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    code = generate_code()
    success = create_hotspot_user(username, code)
    
    if success:
        vouchers.append({"username": username, "code": code})
        return jsonify({"voucher": code})
    else:
        return jsonify({"error": "Failed to create voucher"}), 500

@app.route("/admin")
def admin():
    return render_template("admin.html", vouchers=vouchers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
