from flask import Flask, request, jsonify, render_template_string, Response
import json
import os
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot

app = Flask(__name__)

DATA_FILE = "customers.json"

# قراءة اسم المستخدم وكلمة السر من متغيرات البيئة BASIC_AUTH_USERNAME و BASIC_AUTH_PASSWORD
USERNAME = os.getenv("BASIC_AUTH_USERNAME", "admin")
PASSWORD = os.getenv("BASIC_AUTH_PASSWORD", "1234")

TELEGRAM_TOKEN = "8003548627:AAHpSyXnVK-Nyz-oCzPUddcXQ9PQQPSAeQo"  # توكن البوت
CHAT_ID = 7777263915  # ايدي حسابك في تلغرام

bot = Bot(token=TELEGRAM_TOKEN)

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

def load_customers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_customers(customers):
    with open(DATA_FILE, "w") as f:
        json.dump(customers, f, indent=2)

@app.route("/")
def index():
    customers = load_customers()
    return render_template_string(HTML_TEMPLATE, customers=customers)

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

    join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_customer = {
        "name": name,
        "phone": phone,
        "app_name": app_name,
        "join_date": join_date,
        "paid": False
    }
    customers.append(new_customer)
    save_customers(customers)
    return jsonify({"success": True})

@app.route("/delete_customer", methods=["POST"])
def delete_customer():
    data = request.json
    phone = data.get("phone", "").strip()
    customers = load_customers()
    new_list = [c for c in customers if c["phone"] != phone]
    if len(new_list) == len(customers):
        return jsonify({"success": False, "message": "Customer not found."})
    save_customers(new_list)
    return jsonify({"success": True})

@app.route("/mark_paid", methods=["POST"])
def mark_paid():
    data = request.json
    phone = data.get("phone", "").strip()
    customers = load_customers()
    found = False
    for c in customers:
        if c["phone"] == phone:
            c["paid"] = True
            found = True
            break
    if not found:
        return jsonify({"success": False, "message": "Customer not found."})
    save_customers(customers)
    return jsonify({"success": True})

def send_telegram_reminder():
    try:
        # يمكن تعديل الرسالة حسب الحاجة
        message = "تذكير يومي: لا تنسى مراجعة قائمة العملاء وتحديث الحالات."
        bot.send_message(chat_id=CHAT_ID, text=message)
        print("Telegram reminder sent.")
    except Exception as e:
        print("Error sending Telegram message:", e)

# ضبط الجدولة - كل يوم الساعة 8 صباحًا بتوقيت بيروت
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Beirut"))
scheduler.add_job(send_telegram_reminder, 'cron', hour=8, minute=0)
scheduler.start()

# HTML_TEMPLATE (كما أرسلته سابقاً) ...

# (ضع هنا قالب HTML كامل كما في كودك السابق)

if __name__ == "__main__":
    app.run(debug=True)
