from datetime import datetime, timedelta
# ...

@app.route("/add_customer", methods=["POST"])
def add_customer():
    data = request.json
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    app_name = data.get("app_name", "").strip()

    if not name or not phone or not app_name:
        return jsonify({"success": False, "message": "Missing fields."})

    customers = load_customers()

    if any(c["phone"] == phone for c in customers):
        return jsonify({"success": False, "message": "Customer with this phone already exists."})

    join_date = datetime.now()
    end_date = join_date + timedelta(days=30)  # مثلاً الاشتراك 30 يوم

    new_customer = {
        "name": name,
        "phone": phone,
        "app_name": app_name,
        "join_date": join_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),  # جديد
        "paid": False
    }
    customers.append(new_customer)
    save_customers(customers)
    return jsonify({"success": True})

# ...

# داخل قالب HTML في جدول العملاء، أضف عمود جديد لـ End Date

HTML_TEMPLATE = '''
<!-- أضف هذا العنوان في جدول الأعمدة -->
<th>End Date</th>

<!-- داخل تكرار العملاء -->
<td data-label="Join Date">{{ customer.join_date }}</td>
<td data-label="End Date">{{ customer.end_date }}</td>  <!-- جديد -->

<!-- بقية الجدول كما هو -->
'''
