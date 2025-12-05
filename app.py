
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

DB = os.path.join(os.path.dirname(__file__), 'greenlife.db')
app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-this'  # change for production

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB):
        conn = get_db()
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        # add demo users
        cur = conn.cursor()
        cur.execute("""INSERT INTO users (name,email,password,role) VALUES 
            ('Alice Client','alice@example.com', ?, 'client'),
            ('Bob Therapist','bob@example.com', ?, 'therapist'),
            ('Admin','admin@example.com', ?, 'admin')""", 
            (generate_password_hash('client123'), generate_password_hash('therapist123'), generate_password_hash('admin123')))
        conn.commit()
        conn.close()

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        conn = get_db()
        g.user = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)',
                         (name,email,generate_password_hash(password),role))
            conn.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error: ' + str(e))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Welcome, ' + user['name'])
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    role = g.user['role']
    if role == 'client':
        conn = get_db()
        appointments = conn.execute('SELECT a.*, u.name as therapist_name FROM appointments a LEFT JOIN users u ON a.therapist_id = u.id WHERE a.client_id=?', (g.user['id'],)).fetchall()
        return render_template('dashboard_client.html', appointments=appointments)
    elif role == 'therapist':
        conn = get_db()
        appointments = conn.execute('SELECT a.*, u.name as client_name FROM appointments a LEFT JOIN users u ON a.client_id = u.id WHERE a.therapist_id=?', (g.user['id'],)).fetchall()
        return render_template('dashboard_therapist.html', appointments=appointments)
    else:
        conn = get_db()
        users = conn.execute('SELECT * FROM users').fetchall()
        appointments = conn.execute('SELECT a.*, c.name as client_name, t.name as therapist_name FROM appointments a LEFT JOIN users c ON a.client_id=c.id LEFT JOIN users t ON a.therapist_id=t.id').fetchall()
        return render_template('admin.html', users=users, appointments=appointments)

@app.route('/book', methods=['GET','POST'])
def book():
    if not g.user or g.user['role'] != 'client':
        flash('Clients only: please login as a client to book.')
        return redirect(url_for('login'))
    conn = get_db()
    therapists = conn.execute('SELECT * FROM users WHERE role="therapist"').fetchall()
    if request.method=='POST':
        therapist_id = request.form['therapist_id']
        date = request.form['date']
        notes = request.form.get('notes','')
        conn.execute('INSERT INTO appointments (client_id,therapist_id,date,notes,status) VALUES (?,?,?,?,?)',
                     (g.user['id'], therapist_id, date, notes, 'Pending'))
        conn.commit()
        flash('Appointment requested')
        return redirect(url_for('dashboard'))
    return render_template('book.html', therapists=therapists)

@app.route('/respond/<int:appt_id>', methods=['POST'])
def respond(appt_id):
    if not g.user or g.user['role'] not in ('therapist','admin'):
        flash('Not authorized')
        return redirect(url_for('login'))
    action = request.form['action']
    conn = get_db()
    if action == 'accept':
        conn.execute('UPDATE appointments SET status="Accepted" WHERE id=?', (appt_id,))
    elif action == 'reject':
        conn.execute('UPDATE appointments SET status="Rejected" WHERE id=?', (appt_id,))
    conn.commit()
    flash('Status updated')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
