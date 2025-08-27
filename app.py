import os
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            service TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        service = request.form['service']
        message = request.form['message']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO clients (name, email, company, service, message) VALUES (?, ?, ?, ?, ?)',
                  (name, email, company, service, message))
        conn.commit()
        conn.close()

        return redirect('/thankyou')

    # Data for sections
    services = [
        "Email Campaign Creation",
        "Welcome/Onboarding Sequences",
        "Newsletters & Automation",
        "Analytics & Reporting"
    ]
    advantages = [
        "Personalized Strategy",
        "Creativity & Design",
        "Accountability & Reporting",
        "Affordable & Flexible"
    ]
    how_it_works = [
        "Sign up for a free trial",
        "Approve the campaign strategy",
        "Emails are sent to subscribers",
        "Receive detailed performance report"
    ]
    testimonials = [
        {"name": "John D.", "text": "Aarya created amazing email campaigns that increased our sales by 30%!"},
        {"name": "Sara P.", "text": "Professional, creative, and easy to work with."}
    ]

    return render_template('index.html', services=services, advantages=advantages,
                           how_it_works=how_it_works, testimonials=testimonials)

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

# PayPal logging endpoint
@app.route('/paypal-success', methods=['POST'])
def paypal_success():
    data = request.json
    email = data.get("email")
    services = data.get("services")  # list of services
    name = data.get("name", "Paid Client")
    company = data.get("company", "")

    if not email or not services:
        return jsonify({"status": "error", "message": "Missing email or services"}), 400

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for service in services:
        c.execute('INSERT INTO clients (name, email, company, service, message) VALUES (?, ?, ?, ?, ?)',
                  (name, email, company, service, "Paid via PayPal"))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/success')
def success():
    return render_template('thankyou.html')

@app.route('/cancel')
def cancel():
    return render_template('thankyou.html')  # Can create separate cancel page if desired

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
