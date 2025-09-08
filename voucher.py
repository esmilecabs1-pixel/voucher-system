from flask import Flask, render_template, request
from routeros_api import RouterOsApiPool
import random
import string

app = Flask(__name__)

# MikroTik connection details (replace with your real values or use .env)
MIKROTIK_IP = "172.17.0.1"
MIKROTIK_USER = "cabigas"
MIKROTIK_PASS = "Esmilefb@Genuin3"
MIKROTIK_PORT = 8728

def generate_voucher_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def connect_mikrotik():
    try:
        api_pool = RouterOsApiPool(
            MIKROTIK_IP, username=MIKROTIK_USER, password=MIKROTIK_PASS, port=MIKROTIK_PORT, plaintext_login=True
        )
        return api_pool.get_api(), api_pool
    except Exception as e:
        print(f"Failed to connect to MikroTik: {e}")
        return None, None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/generate", methods=["POST"])
def generate():
    api, api_pool = connect_mikrotik()
    if not api:
        return render_template("error.html", message="MikroTik unreachable. Please try again later.")

    voucher = generate_voucher_code()
    try:
        user_resource = api.get_resource("/ip/hotspot/user")
        user_resource.add(name=voucher, password=voucher, profile="default")
        api_pool.disconnect()
        return render_template("gcash_success.html", voucher=voucher)
    except Exception as e:
        print(f"Error adding voucher to MikroTik: {e}")
        return render_template("error.html", message="Failed to add voucher to MikroTik.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
