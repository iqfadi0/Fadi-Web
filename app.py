from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import datetime

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

@app.route("/")
def home():
    customers = load_customers()
    # نرسل البيانات للصفحة الرئيسية
    return render_template("index.html", customers=customers)

@app.route("/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return "Name is required!", 400
        customers = load_customers()
        if name in customers:
            return "Customer already exists!", 400
        join_date = datetime.date.today().isoformat()
        customers[name] = {"join_date": join_date, "paid": False}
        save_customers(customers)
        return redirect(url_for("home"))
    return render_template("add.html")

@app.route("/delete/<name>", methods=["POST"])
def delete_customer(name):
    customers = load_customers()
    if name in customers:
        del customers[name]
        save_customers(customers)
    return redirect(url_for("home"))

@app.route("/pay/<name>", methods=["POST"])
def confirm_payment(name):
    customers = load_customers()
    if name in customers:
        customers[name]["paid"] = True
        save_customers(customers)
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
