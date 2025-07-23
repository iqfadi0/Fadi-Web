from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "customers.json"

def load_customers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_customers(customers):
    with open(DATA_FILE, "w") as f:
        json.dump(customers, f, indent=2)

@app.route("/")
def home():
    customers = load_customers()
    return render_template("index.html", customers=customers)

@app.route("/add", methods=["POST"])
def add_customer():
    name = request.form.get("name").strip()
    phone = request.form.get("phone").strip()
    app_name = request.form.get("app_name").strip()
    if not name or not phone or not app_name:
        return redirect(url_for('home'))

    customers = load_customers()
    # إضافة العميل الجديد مع تاريخ اليوم وحالة الدفع False
    customers.append({
        "name": name,
        "phone": phone,
        "app_name": app_name,
        "join_date": datetime.today().strftime("%Y-%m-%d"),
        "paid": False
    })
    save_customers(customers)
    return redirect(url_for('home'))

@app.route("/delete/<int:index>", methods=["POST"])
def delete_customer(index):
    customers = load_customers()
    if 0 <= index < len(customers):
        customers.pop(index)
        save_customers(customers)
    return redirect(url_for('home'))

@app.route("/toggle_paid/<int:index>", methods=["POST"])
def toggle_paid(index):
    customers = load_customers()
    if 0 <= index < len(customers):
        customers[index]["paid"] = not customers[index]["paid"]
        save_customers(customers)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
