from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import date

app = Flask(__name__)

DATA_FILE = "customers.json"

def load_customers():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_customers(customers):
    with open(DATA_FILE, "w") as f:
        json.dump(customers, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = load_customers()
    return jsonify(customers)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    if not name or not phone:
        return jsonify({"error": "Name and phone required"}), 400

    customers = load_customers()
    if name in customers:
        return jsonify({"error": "Customer already exists"}), 400

    customers[name] = {
        "phone": phone,
        "join_date": str(date.today()),
        "paid": False
    }
    save_customers(customers)
    return jsonify({"message": f"Customer {name} added."})

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    data = request.json
    name = data.get('name')
    customers = load_customers()
    if name not in customers:
        return jsonify({"error": "Customer not found"}), 404

    del customers[name]
    save_customers(customers)
    return jsonify({"message": f"Customer {name} deleted."})

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    data = request.json
    name = data.get('name')
    customers = load_customers()
    if name not in customers:
        return jsonify({"error": "Customer not found"}), 404

    customers[name]["paid"] = True
    save_customers(customers)
    return jsonify({"message": f"Payment confirmed for {name}."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
