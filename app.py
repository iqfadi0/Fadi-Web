from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
customers = []

@app.route('/')
def index():
    return render_template('index.html', customers=customers)

@app.route('/add', methods=['POST'])
def add_customer():
    name = request.form['name']
    phone = request.form['phone']
    app_name = request.form['app']
    date_added = datetime.now().strftime('%Y-%m-%d %H:%M')
    customers.append({
        'name': name,
        'phone': phone,
        'app': app_name,
        'date': date_added,
        'paid': False
    })
    return redirect(url_for('index'))

@app.route('/paid/<int:index>')
def mark_paid(index):
    customers[index]['paid'] = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
