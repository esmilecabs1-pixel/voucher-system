from flask import Flask, render_template_string, request, flash
import os

app = Flask(__name__, template_folder=os.getcwd())  # Use current folder for templates
app.secret_key = "YOUR_SECRET_KEY"  # Replace with your secret key

# Load HTML files as strings
def load_html(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

@app.route("/", methods=["GET", "POST"])
def index():
    html_content = load_html("index.html")
    return render_template_string(html_content)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    html_content = load_html("admin.html")
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
