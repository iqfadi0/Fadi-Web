from flask import Flask, render_template, request, jsonify
import json
import datetime
import os

app = Flask(__name__)

CUSTOMERS_FILE = "customers.json"

def load_customers():
    if not os.path.exists(CUSTOMERS_FILE):
        return []
    with open(CUSTOMERS_FILE, "r") as f:
        return json.load(f)

def save_customers(customers):
    with open(CUSTOMERS_FILE, "w") as f:
        json.dump(customers, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = load_customers()
    return jsonify(customers)

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.json
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    if not name or not phone:
        return jsonify({"error": "Name and phone are required"}), 400

    customers = load_customers()

    # تحقق إذا العميل موجود مسبقاً
    if any(c['name'].lower() == name.lower() for c in customers):
        return jsonify({"error": "Customer already exists"}), 400

    new_customer = {
        "name": name,
        "phone": phone,
        "join_date": datetime.date.today().isoformat(),
        "paid": False
    }
    customers.append(new_customer)
    save_customers(customers)
    return jsonify({"message": "Customer added successfully"}), 201

@app.route('/api/customers/<name>/delete', methods=['POST'])
def delete_customer(name):
    customers = load_customers()
    filtered = [c for c in customers if c['name'].lower() != name.lower()]
    if len(filtered) == len(customers):
        return jsonify({"error": "Customer not found"}), 404

    save_customers(filtered)
    return jsonify({"message": "Customer deleted successfully"})

@app.route('/api/customers/<name>/paid', methods=['POST'])
def mark_paid(name):
    customers = load_customers()
    found = False
    for c in customers:
        if c['name'].lower() == name.lower():
            c['paid'] = True
            found = True
            break

    if not found:
        return jsonify({"error": "Customer not found"}), 404

    save_customers(customers)
    return jsonify({"message": f"Payment confirmed for {name}."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
