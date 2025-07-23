from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "customers.json"

def load_customers():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            f.write("[]")
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_customers(customers):
    with open(DATA_FILE, "w") as f:
        json.dump(customers, f, indent=2)

@app.route("/")
def home():
    customers = load_customers()
    return render_template("index.html", customers=customers)

@app.route("/add_customer", methods=["POST"])
def add_customer():
    data = request.get_json()
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    if not name or not phone:
        return jsonify({"success": False, "message": "Name and phone are required."})

    customers = load_customers()
    # Check if customer already exists by name or phone
    for c in customers:
        if c["name"].lower() == name.lower() or c["phone"] == phone:
            return jsonify({"success": False, "message": "Customer already exists."})

    new_customer = {
        "name": name,
        "phone": phone,
        "join_date": datetime.now().strftime("%Y-%m-%d"),
        "paid": False
    }
    customers.append(new_customer)
    save_customers(customers)
    return jsonify({"success": True, "customer": new_customer})

@app.route("/delete_customer", methods=["POST"])
def delete_customer():
    data = request.get_json()
    phone = data.get("phone", "").strip()
    if not phone:
        return jsonify({"success": False, "message": "Phone is required."})

    customers = load_customers()
    new_customers = [c for c in customers if c["phone"] != phone]

    if len(customers) == len(new_customers):
        return jsonify({"success": False, "message": "Customer not found."})

    save_customers(new_customers)
    return jsonify({"success": True})

@app.route("/mark_paid", methods=["POST"])
def mark_paid():
    data = request.get_json()
    phone = data.get("phone", "").strip()
    if not phone:
        return jsonify({"success": False, "message": "Phone is required."})

    customers = load_customers()
    for c in customers:
        if c["phone"] == phone:
            c["paid"] = True
            save_customers(customers)
            return jsonify({"success": True})

    return jsonify({"success": False, "message": "Customer not found."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
