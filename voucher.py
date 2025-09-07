from flask import Flask, render_template, request, jsonify
import os
import random
import string
import routeros_api

app = Flask(__name__, template_folder='.')  # Use current folder for HTML

# MikroTik connection settings
RO_HOST = os.getenv("RO_HOST", "172.17.0.1")
RO_USER = os.getenv("RO_USER", "benjor")
RO_PASS = os.getenv("RO_PASS", "qpwoieur")

def connect_mikrotik():
    try:
        connection = routeros_api.RouterOsApiPool(
            RO_HOST, username=RO_USER, password=RO_PASS, plaintext_login=True
        )
        api = connection.get_api()
        return connection, api
    except Exception as e:
        print("MikroTik connection failed:", e)
        return None, None

def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    if request.method == "POST":
        connection, api = connect_mikrotik()
        if not api:
            return "MikroTik unreachable. Cannot generate voucher.", 500
        
        code = generate_code()
        try:
            api.get_resource('/ip/hotspot/user').add(name=code, password=code, profile='default')
            connection.disconnect()
        except Exception as e:
            print("Failed to add voucher:", e)
            return f"Voucher generated but failed to add to MikroTik: {code}", 500
    
    return render_template("index.html", code=code)

@app.route("/admin")
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
