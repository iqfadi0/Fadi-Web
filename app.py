from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "customers.json"

# تحميل العملاء
def load_customers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

# حفظ العملاء
def save_customers(customers):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, indent=2, ensure_ascii=False)

@app.route("/")
def home():
    return render_template("index.html")

# API لجلب العملاء
@app.route("/api/customers", methods=["GET"])
def get_customers():
    customers = load_customers()
    return jsonify(customers)

# API لإضافة عميل جديد
@app.route("/api/customers", methods=["POST"])
def add_customer():
    data = request.get_json()
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    if not name or not phone:
        return jsonify({"success": False, "message": "الاسم ورقم الهاتف مطلوبان"}), 400
    
    customers = load_customers()
    # تحقق من عدم تكرار الاسم أو الرقم
    for c in customers:
        if c["name"].lower() == name.lower():
            return jsonify({"success": False, "message": "العميل موجود مسبقًا"}), 400
        if c["phone"] == phone:
            return jsonify({"success": False, "message": "رقم الهاتف مستخدم مسبقًا"}), 400
    
    new_customer = {
        "name": name,
        "phone": phone,
        "join_date": datetime.now().strftime("%Y-%m-%d"),
        "paid": False
    }
    customers.append(new_customer)
    save_customers(customers)
    return jsonify({"success": True, "message": "تم إضافة العميل بنجاح"})

# API لتحديث حالة الدفع
@app.route("/api/customers/<phone>/paid", methods=["POST"])
def mark_paid(phone):
    customers = load_customers()
    for c in customers:
        if c["phone"] == phone:
            c["paid"] = True
            save_customers(customers)
            return jsonify({"success": True, "message": "تم تحديث حالة الدفع"})
    return jsonify({"success": False, "message": "العميل غير موجود"}), 404

# API لحذف عميل
@app.route("/api/customers/<phone>", methods=["DELETE"])
def delete_customer(phone):
    customers = load_customers()
    new_customers = [c for c in customers if c["phone"] != phone]
    if len(new_customers) == len(customers):
        return jsonify({"success": False, "message": "العميل غير موجود"}), 404
    save_customers(new_customers)
    return jsonify({"success": True, "message": "تم حذف العميل"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
