import os
from flask import Flask, render_template, request, redirect, jsonify, Response
import sqlite3
import io, csv

app = Flask(__name__)

# Admin credentials (change these in Render environment variables for security)
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "adminpass")

def check_auth(auth):
    if not auth:
        return False
    return auth.username == ADMIN_USER and auth.password == ADMIN_PASS

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
            message TEXT,
            paid INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Free trial submission (single service)
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        company = request.form.get('company','').strip()
        service = request.form.get('service','').strip()
        message = request.form.get('message','').strip()

        if not name or not email or not service:
            return redirect('/?error=missing')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO clients (name, email, company, service, message, paid) VALUES (?, ?, ?, ?, ?, ?)',
                  (name, email, company, service, message, 0))
        conn.commit()
        conn.close()

        return redirect('/thankyou')

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

@app.route('/paypal_capture', methods=['POST'])
def paypal_capture():
    data = request.json
    name = data.get('name','').strip()
    email = data.get('email','').strip()
    company = data.get('company','').strip()
    services = data.get('services', [])

    if not name or not email or not services:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for service in services:
        c.execute('INSERT INTO clients (name, email, company, service, paid) VALUES (?, ?, ?, ?, ?)',
                  (name, email, company, service, 1))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')


# Admin: View signups in browser (protected by Basic Auth)
@app.route('/admin/signups')
def admin_signups():
    auth = request.authorization
    if not check_auth(auth):
        return Response('Login required', 401, {'WWW-Authenticate': 'Basic realm="Signups"'})

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, company, service, message, paid FROM clients ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return render_template('signups.html', signups=rows)

# Admin: Download CSV (protected)
@app.route('/admin/signups.csv')
def admin_signups_csv():
    auth = request.authorization
    if not check_auth(auth):
        return Response('Login required', 401, {'WWW-Authenticate': 'Basic realm="Signups"'})

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, company, service, message, paid FROM clients ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id','name','email','company','service','message','paid'])
    writer.writerows(rows)
    csv_data = output.getvalue()
    return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=signups.csv'})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
