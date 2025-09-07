from flask import Flask, render_template, request, flash
from routeros_api import RouterOsApiPool
import random
import string
import os

# Tell Flask templates are in the same folder
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = os.urandom(24)

# MikroTik connection settings
ROUTER_HOST = "172.17.0.1"  # change to your MikroTik IP
ROUTER_USER = "benjor"
ROUTER_PASS = "qpwoieur"
ROUTER_PORT = 8728  # default API port

def generate_voucher(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def add_voucher_to_mikrotik(voucher_code):
    try:
        api = RouterOsApiPool(
            host=ROUTER_HOST,
            username=ROUTER_USER,
            password=ROUTER_PASS,
            port=ROUTER_PORT,
            plaintext_login=True
        )
        router = api.get_api()
        router.get_resource('/ip/hotspot/user').add(
            name=voucher_code,
            password=voucher_code,
            profile='default',
            limit_uptime='1h'
        )
        api.disconnect()
        print(f"[SUCCESS] Voucher '{voucher_code}' added to MikroTik")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to add voucher '{voucher_code}' to MikroTik:", e)
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    voucher_code = ""
    if request.method == 'POST':
        voucher_code = generate_voucher()
        success = add_voucher_to_mikrotik(voucher_code)
        if success:
            flash(f"Voucher generated and added: {voucher_code}", "success")
        else:
            flash(f"Voucher generated but failed to add to MikroTik: {voucher_code}", "danger")
    return render_template("index.html", voucher_code=voucher_code)

@app.route('/admin')
def admin():
    return render_template("admin.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
