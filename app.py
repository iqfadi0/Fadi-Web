from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime
import pytz
import threading
import time
import telegram

app = Flask(__name__)

DATA_FILE = "customers.json"
TELEGRAM_TOKEN = "8003548627:AAHpSyXnVK-Nyz-oCzPUddcXQ9PQQPSAeQo"
OWNER_CHAT_ID = 7777263915  # حسابك الشخصي

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
    now = datetime.now(pytz.timezone("Asia/Beirut")).strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", customers=customers, now=now)

@app.route("/add", methods=["POST"])
def add_customer():
    customers = load_customers()
    new_customer = {
        "name": request.form["name"],
        "phone": request.form["phone"],
        "paid": request.form.get("paid") == "on",
        "start_date": request.form["start_date"],
        "end_date": request.form["end_date"]
    }
    customers.append(new_customer)
    save_customers(customers)
    return redirect("/")

@app.route("/toggle/<int:index>")
def toggle_paid(index):
    customers = load_customers()
    customers[index]["paid"] = not customers[index]["paid"]
    save_customers(customers)
    return redirect("/")

@app.route("/delete/<int:index>")
def delete_customer(index):
    customers = load_customers()
    customers.pop(index)
    save_customers(customers)
    return redirect("/")

def send_daily_reminder():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        now = datetime.now(pytz.timezone("Asia/Beirut"))
        if now.hour == 9 and now.minute == 0:
            customers = load_customers()
            unpaid = [c for c in customers if not c["paid"]]
            if unpaid:
                message = "📋 المشتركين الذين لم يدفعوا:\n\n"
                for c in unpaid:
                    message += f"👤 الاسم: {c['name']}\n📞 الرقم: {c['phone']}\n📆 من: {c['start_date']} إلى: {c['end_date']}\n\n"
                try:
                    bot.send_message(chat_id=OWNER_CHAT_ID, text=message)
                except Exception as e:
                    print("Error sending Telegram message:", e)
        time.sleep(60)

# بدء مهمة التذكير في الخلفية
threading.Thread(target=send_daily_reminder, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
