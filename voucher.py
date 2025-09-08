import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for
from routeros_api import RouterOsApiPool, exceptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Explicitly set template_folder to current directory
app = Flask(__name__, template_folder='.')

# MikroTik connection details
MT_IP = os.getenv("MT_IP", "172.17.0.1")
MT_USER = os.getenv("MT_USER", "cabigas")
MT_PASS = os.getenv("MT_PASS", "Esmilefb@Genuin3")

def connect_to_mikrotik():
    try:
        api_pool = RouterOsApiPool(
            MT_IP,
            username=MT_USER,
            password=MT_PASS,
            plaintext_login=True
        )
        return api_pool.get_api()
    except exceptions.RouterOsApiConnectionError:
        return None

def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/generate", methods=["POST"])
def generate():
    api = connect_to_mikrotik()
    if not api:
        return render_template("error.html", message="MikroTik unreachable. Please try again later.")

    code = generate_code()

    try:
        user_manager = api.get_resource("/ip/hotspot/user")
        user_manager.add(
            name=code,
            password=code,
            profile="default"
        )
        return render_template("gcash_success.html", voucher=code)
    except Exception as e:
        return render_template("error.html", message=f"Failed to add voucher: {e}")

@app.route("/gcash")
def gcash():
    return render_template("gcash.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
