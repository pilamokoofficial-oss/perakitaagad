from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
import os
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'demo_data.sqlite'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not DB_PATH.exists():
        conn = get_db()
        c = conn.cursor()
        c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            balance_cents INTEGER DEFAULT 0,
            apr_percent REAL DEFAULT 5.0,
            created_at TEXT
        )
        ''')
        conn.commit()
        conn.close()

app = Flask(__name__)
app.secret_key = 'demo-secret-key'  # DO NOT use this in production

init_db()

def format_currency_cents(cents):
    return f"₱{(Decimal(cents) / 100).quantize(Decimal('0.01'))}"

@app.route('/')
def index():
    user = None
    if session.get('username'):
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (session['username'],))
        user = c.fetchone()
        conn.close()
    return render_template('index.html', user=user, format_currency=format_currency_cents)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        uname = request.form.get('username').strip()
        if not uname:
            flash('Username required', 'error')
            return redirect(url_for('signup'))
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, created_at) VALUES (?,?)', (uname, datetime.utcnow().isoformat()))
            conn.commit()
            session['username'] = uname
            flash('Account created (demo)', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash('Username already exists or error', 'error')
            return redirect(url_for('signup'))
        finally:
            conn.close()
    return render_template('login.html', action='Sign Up')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username').strip()
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (uname,))
        u = c.fetchone()
        conn.close()
        if u:
            session['username'] = uname
            flash('Logged in (demo)', 'success')
            return redirect(url_for('index'))
        else:
            flash('User not found', 'error')
            return redirect(url_for('login'))
    return render_template('login.html', action='Login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out', 'info')
    return redirect(url_for('index'))

@app.route('/deposit', methods=['POST'])
def deposit():
    if not session.get('username'):
        flash('Login first', 'error')
        return redirect(url_for('login'))
    amount = request.form.get('amount')
    try:
        amt = Decimal(amount)
        if amt <= 0:
            raise ValueError('positive only')
    except:
        flash('Invalid amount', 'error')
        return redirect(url_for('index'))
    cents = int((amt * 100).to_integral_value(ROUND_DOWN))
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET balance_cents = balance_cents + ? WHERE username = ?', (cents, session['username']))
    conn.commit()
    conn.close()
    flash('Deposit simulated (demo). No real money moved.', 'success')
    return redirect(url_for('index'))

@app.route('/set-apr', methods=['POST'])
def set_apr():
    if not session.get('username'):
        flash('Login first', 'error')
        return redirect(url_for('login'))
    apr = request.form.get('apr')
    try:
        apr_f = float(apr)
    except:
        flash('Invalid APR', 'error')
        return redirect(url_for('index'))
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET apr_percent = ? WHERE username = ?', (apr_f, session['username']))
    conn.commit()
    conn.close()
    flash('APR updated (demo only)', 'success')
    return redirect(url_for('index'))

@app.route('/accrue', methods=['POST'])
def accrue():
    # Apply one day of accrual to the logged-in user's balance (simulated)
    if not session.get('username'):
        flash('Login first', 'error')
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT balance_cents, apr_percent FROM users WHERE username = ?', (session['username'],))
    row = c.fetchone()
    if not row:
        conn.close()
        flash('User not found', 'error')
        return redirect(url_for('index'))
    balance = Decimal(row['balance_cents']) / 100
    apr = Decimal(row['apr_percent'])
    daily_rate = (apr / Decimal(100)) / Decimal(365)
    interest = (balance * daily_rate).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    interest_cents = int((interest * 100).to_integral_value(ROUND_DOWN))
    if interest_cents > 0:
        c.execute('UPDATE users SET balance_cents = balance_cents + ? WHERE username = ?', (interest_cents, session['username']))
        conn.commit()
    conn.close()
    flash(f'Applied daily accrual (demo): {interest} added.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run local dev server
    app.run(debug=True)
