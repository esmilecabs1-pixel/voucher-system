from flask import Flask, render_template, request, redirect, url_for
import os
import random
import string

# Flask app setup; templates in the same folder as voucher.py
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

# In-memory store for vouchers
vouchers = []

# Home route for generating vouchers
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if username:
            # Generate random 8-character voucher code
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # Store voucher
            vouchers.append({"username": username, "code": code})
            # Render template with generated code
            return render_template("index.html", username=username, code=code)
    # GET request renders page with empty form
    return render_template("index.html")

# Admin route to view all generated vouchers
@app.route("/admin")
def admin():
    return render_template("admin.html", vouchers=vouchers)

# Run app locally
if __name__ == "__main__":
    app.run(debug=True)
