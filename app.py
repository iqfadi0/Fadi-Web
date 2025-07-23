from flask import Flask, render_template, request, jsonify
from flask_basicauth import BasicAuth
import json
import os
import datetime
import pytz

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = os.getenv('BASIC_AUTH_USERNAME', 'admin')
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('BASIC_AUTH_PASSWORD', 'password')
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

DATA_FILE = "customers.json"

def load_customers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_customers(customers):
    with open(DATA_FILE, "w") as f:
        json.dump(customers, f, indent=2)

def get_local_today():
    tz = pytz.timezone('Asia/Beirut')
    now = datetime.datetime.now(tz)
    return now.strftime("%d-%m-%Y")

@app.route("/")
def home():
    customers = load_customers()
    return render_template("index.html", customers=customers)

@app.route("/add_customer", methods=["POST"])
def add_customer():
    data = request.json
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    app_name = data.get("app_name", "").strip()

    if not name or not phone or not app_name:
        return jsonify({"success": False, "message": "Name, phone, and app name are required."})

    customers = load_customers()
    for cust in customers:
        if cust["phone"] == phone:
            return jsonify({"success": False, "message": "Customer with this phone already exists."})

    today = get_local_today()
    customers.append({
        "name": name,
        "phone": phone,
        "app_name": app_name,
        "join_date": today,
        "paid": False
    })

    save_customers(customers)
    return jsonify({"success": True, "message": "Customer added successfully."})

@app.route("/delete_customer", methods=["POST"])
def delete_customer():
    data = request.json
    phone = data.get("phone", "").strip()
    if not phone:
        return jsonify({"success": False, "message": "Phone is required."})

    customers = load_customers()
    customers = [c for c in customers if c["phone"] != phone]
    save_customers(customers)
    return jsonify({"success": True, "message": "Customer deleted successfully."})

@app.route("/mark_paid", methods=["POST"])
def mark_paid():
    data = request.json
    phone = data.get("phone", "").strip()
    if not phone:
        return jsonify({"success": False, "message": "Phone is required."})

    customers = load_customers()
    for cust in customers:
        if cust["phone"] == phone:
            cust["paid"] = True
            save_customers(customers)
            return jsonify({"success": True, "message": f"{cust['name']} marked as paid."})

    return jsonify({"success": False, "message": "Customer not found."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
