from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
customers = []

@app.route('/')
def index():
    return render_template('index.html', customers=customers)

@app.route('/add', methods=['POST'])
def add_customer():
    name = request.form.get('name')
    phone = request.form.get('phone')
    app_name = request.form.get('app_name')  # New field
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    customers.append({'name': name, 'phone': phone, 'app_name': app_name, 'date': date, 'paid': False})
    return redirect(url_for('index'))

@app.route('/pay/<int:index>', methods=['POST'])
def pay(index):
    customers[index]['paid'] = True
    return redirect(url_for('index'))

@app.route('/delete/<int:index>', methods=['POST'])
def delete_customer(index):
    customers.pop(index)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
