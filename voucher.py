from flask import Flask, render_template, request, jsonify
from routeros_api import RouterOsApiPool, ApiException
import random, string, os

app = Flask(__name__)

# MikroTik connection settings
MIKROTIK_HOST = os.getenv("MIKROTIK_HOST", "172.17.0.1")
MIKROTIK_USER = os.getenv("MIKROTIK_USER", "benjor")
MIKROTIK_PASS = os.getenv("qpwoieur", "")

def generate_voucher(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_to_mikrotik(username, password, profile='default'):
    try:
        connection = RouterOsApiPool(MIKROTIK_HOST, username=MIKROTIK_USER, password=MIKROTIK_PASS, plaintext_login=True)
        api = connection.get_api()
        api.get_resource('/ip/hotspot/user').add(name=username, password=password, profile=profile)
        connection.disconnect()
        return True
    except ApiException:
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    username = generate_voucher()
    success = add_to_mikrotik(username, username)
    if success:
        return jsonify({"status": "success", "voucher": username})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to MikroTik"}), 500

@app.route("/admin")
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
