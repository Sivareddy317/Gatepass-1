#!/usr/bin/env python3
"""
College Gate Pass Management System
Simplified with 2 Students and Fixed Admin Dashboard
** Updated with Attendance Upload and Patched Search **
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
import sqlite3
import logging
import os
from datetime import datetime
from functools import wraps
import traceback
import re
import jinja2
import io
import csv
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'cbit-gate-pass-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)

def init_db():
    """Initialize database with minimal setup"""
    try:
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        # Drop existing tables to start fresh
        c.execute('DROP TABLE IF EXISTS users')
        c.execute('DROP TABLE IF EXISTS gate_passes')
        c.execute('DROP TABLE IF EXISTS attendance')
        
        # Users table
        c.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT,
            roll_number TEXT,
            assigned_range_start TEXT,
            assigned_range_end TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Gate passes table
        c.execute('''CREATE TABLE gate_passes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT NOT NULL,
            student_name TEXT,
            roll_number TEXT,
            reason TEXT NOT NULL,
            destination TEXT NOT NULL,
            exit_time TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            approver_email TEXT,
            approver_remarks TEXT,
            security_action TEXT,
            exit_marked_at TIMESTAMP,
            return_marked_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Attendance table
        c.execute('''CREATE TABLE attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            percentage REAL NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by TEXT
        )''')
        
        # Insert only 2 students and staff
        sample_users = [
            # Just 2 students as requested
            ('232P1A3317@cbit.edu.in', '232P1A3317', 'student', 'Neha Chopra', '232P1A3317'),
            ('232P1A3346@cbit.edu.in', '232P1A3346', 'student', 'Abhimanyu Rao', '232P1A3346'),
            
            # Staff
            ('approver1@cbit.edu.in', '9182302896', 'approver', 'Mr. Krupasagar', None),
            ('approver2@cbit.edu.in', '9876543210', 'approver', 'Dr. Priya Sharma', None),
            ('security1@cbit.edu.in', '9573239692', 'security', 'Security Officer', None),
            ('admin1@cbit.edu.in', '6300933471', 'admin', 'System Admin', None)
        ]
        
        for user_data in sample_users:
            c.execute('''INSERT INTO users 
                         (email, password, role, name, roll_number) 
                         VALUES (?, ?, ?, ?, ?)''', user_data)
        
        # Set approver assignments
        c.execute('''UPDATE users SET assigned_range_start = '232P1A3317', assigned_range_end = '232P1A3317' 
                     WHERE email = 'approver1@cbit.edu.in' ''')
        c.execute('''UPDATE users SET assigned_range_start = '232P1A3346', assigned_range_end = '232P1A3346' 
                     WHERE email = 'approver2@cbit.edu.in' ''')
        
        # Insert attendance for both students
        c.execute('INSERT INTO attendance (roll_number, percentage, uploaded_by) VALUES (?, ?, ?)', 
                 ('232P1A3317', 85.5, 'system'))
        c.execute('INSERT INTO attendance (roll_number, percentage, uploaded_by) VALUES (?, ?, ?)', 
                 ('232P1A3346', 72.3, 'system'))
        
        # Insert sample gate pass request for testing
        c.execute('''INSERT INTO gate_passes 
                     (student_email, student_name, roll_number, reason, destination, exit_time, approver_email, status) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 ('232P1A3317@cbit.edu.in', 'Neha Chopra', '232P1A3317', 
                  'Medical appointment', 'City Hospital', '2025-09-14T15:46', 'approver1@cbit.edu.in', 'approved'))
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database initialized with 2 students and sample data")
        print("✅ Database setup complete:")
        print("   - 2 students: 232P1A3317, 232P1A3346")
        print("   - 2 approvers, 1 security, 1 admin")
        print("   - Sample attendance data")
        print("   - 1 sample gate pass request")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] != role:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('user_role')
        if role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'approver':
            return redirect(url_for('approver_dashboard'))
        elif role == 'security':
            return redirect(url_for('security_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        logger.info(f"Login attempt: {email}")
        
        if not email or not password:
            flash('Please enter both email and password', 'error')
            return render_template('login.html')
        
        try:
            conn = sqlite3.connect('gate_pass.db')
            c = conn.cursor()
            c.execute('SELECT id, email, password, role, name FROM users WHERE LOWER(email) = ?', (email,))
            user = c.fetchone()
            conn.close()
            
            if user and user[2] == password:
                session['user_id'] = user[0]
                session['user_email'] = user[1]
                session['user_role'] = user[3]
                session['user_name'] = user[4]
                
                logger.info(f"✅ Login successful: {user[1]} as {user[3]}")
                flash(f'Welcome, {user[4]}!', 'success')
                
                if user[3] == 'student':
                    return redirect(url_for('student_dashboard'))
                elif user[3] == 'approver':
                    return redirect(url_for('approver_dashboard'))
                elif user[3] == 'security':
                    return redirect(url_for('security_dashboard'))
                elif user[3] == 'admin':
                    return redirect(url_for('admin_dashboard'))
            else:
                logger.warning(f"❌ Login failed: {email}")
                flash('Invalid email or password', 'error')
                
        except Exception as e:
            logger.error(f'Login error: {e}')
            flash('Login error occurred', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    try:
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        c.execute('''SELECT id, reason, destination, exit_time, status, 
                            approver_remarks, created_at 
                     FROM gate_passes WHERE student_email = ? 
                     ORDER BY created_at DESC''', (session['user_email'],))
        requests = c.fetchall()
        
        c.execute('SELECT roll_number FROM users WHERE email = ?', (session['user_email'],))
        student_data = c.fetchone()
        
        attendance = None
        if student_data:
            c.execute('''SELECT percentage FROM attendance WHERE roll_number = ?''', (student_data[0],))
            attendance_data = c.fetchone()
            if attendance_data:
                attendance = attendance_data[0]
        
        conn.close()
        return render_template('student_dashboard.html', requests=requests, attendance=attendance)
    
    except Exception as e:
        logger.error(f'Student dashboard error: {e}')
        return render_template('student_dashboard.html', requests=[], attendance=None)

@app.route('/student/request', methods=['POST'])
@login_required
@role_required('student')
def submit_request():
    try:
        reason = request.form.get('reason', '').strip()
        destination = request.form.get('destination', '').strip()
        exit_time = request.form.get('exit_time', '')
        
        if not all([reason, destination, exit_time]):
            flash('All fields are required', 'error')
            return redirect(url_for('student_dashboard'))
        
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        c.execute('SELECT roll_number, name FROM users WHERE email = ?', (session['user_email'],))
        student_info = c.fetchone()
        
        if not student_info:
            flash('Student information not found', 'error')
            return redirect(url_for('student_dashboard'))
        
        c.execute('SELECT percentage FROM attendance WHERE roll_number = ?', (student_info[0],))
        attendance_data = c.fetchone()
        attendance = attendance_data[0] if attendance_data else 0
        
        if attendance < 75:
            flash(f'⚠️ Warning: Your attendance is {attendance}%. This will be visible to the approver.', 'warning')
        
        c.execute('''INSERT INTO gate_passes 
                     (student_email, student_name, roll_number, reason, destination, exit_time) 
                     VALUES (?, ?, ?, ?, ?, ?)''',
                 (session['user_email'], student_info[1], student_info[0], reason, destination, exit_time))
        
        roll_number = student_info[0]
        c.execute('''SELECT email FROM users WHERE role = 'approver' 
                     AND ? >= assigned_range_start AND ? <= assigned_range_end''', (roll_number, roll_number))
        approver_data = c.fetchone()
        
        if approver_data:
            c.execute('UPDATE gate_passes SET approver_email = ? WHERE id = last_insert_rowid()', (approver_data[0],))
        
        conn.commit()
        conn.close()
        
        flash('Gate pass request submitted successfully!', 'success')
        
    except Exception as e:
        logger.error(f'Submit request error: {e}')
        flash('Error submitting request', 'error')
    
    return redirect(url_for('student_dashboard'))

@app.route('/approver/dashboard')
@login_required
@role_required('approver')
def approver_dashboard():
    try:
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        c.execute('''SELECT g.id, g.student_email, g.student_name, g.roll_number, 
                            g.reason, g.destination, g.exit_time, g.status, 
                            g.created_at, COALESCE(a.percentage, 0) as attendance
                     FROM gate_passes g
                     LEFT JOIN attendance a ON g.roll_number = a.roll_number
                     WHERE g.approver_email = ? AND g.status = 'pending' 
                     ORDER BY g.created_at ASC''', (session['user_email'],))
        pending_requests = c.fetchall()
        
        c.execute('''SELECT g.id, g.student_name, g.roll_number, g.reason,
                            g.status, g.approver_remarks, g.updated_at,
                            COALESCE(a.percentage, 0) as attendance
                     FROM gate_passes g
                     LEFT JOIN attendance a ON g.roll_number = a.roll_number
                     WHERE g.approver_email = ? AND g.status != 'pending' 
                     ORDER BY g.updated_at DESC LIMIT 10''', (session['user_email'],))
        processed_requests = c.fetchall()
        
        conn.close()
        return render_template('approver_dashboard.html',
                             pending_requests=pending_requests,
                             processed_requests=processed_requests)
    
    except Exception as e:
        logger.error(f'Approver dashboard error: {e}')
        return render_template('approver_dashboard.html', pending_requests=[], processed_requests=[])

@app.route('/approver/action', methods=['POST'])
@login_required
@role_required('approver')
def approver_action():
    try:
        request_id = request.form.get('request_id')
        action = request.form.get('action')
        remarks = request.form.get('remarks', '')
        
        status = 'approved' if action == 'approve' else 'rejected'
        
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        c.execute('''UPDATE gate_passes 
                     SET status = ?, approver_remarks = ?, updated_at = CURRENT_TIMESTAMP 
                     WHERE id = ?''', (status, remarks, request_id))
        conn.commit()
        conn.close()
        
        flash(f'Request {action}d successfully!', 'success')
        
    except Exception as e:
        logger.error(f'Approver action error: {e}')
        flash('Error processing request', 'error')
    
    return redirect(url_for('approver_dashboard'))

@app.route('/security/dashboard')
@login_required
@role_required('security')
def security_dashboard():
    try:
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        # Passes that need action (approved but not exited, or exited but not returned)
        c.execute('''SELECT id, student_name, roll_number, reason, destination, 
                            exit_time, security_action, exit_marked_at, 
                            return_marked_at
                     FROM gate_passes 
                     WHERE status = 'approved' AND (security_action IS NULL OR security_action = 'exited')
                     ORDER BY exit_time ASC''')
        active_passes = c.fetchall()
        
        # History of passes that have been fully processed (returned)
        c.execute('''SELECT id, student_name, roll_number, reason, destination, 
                            exit_time, security_action, exit_marked_at, 
                            return_marked_at
                     FROM gate_passes 
                     WHERE security_action = 'returned'
                     ORDER BY return_marked_at DESC''')
        history_passes = c.fetchall()
        
        conn.close()
        return render_template('security_dashboard.html', 
                               active_passes=active_passes, 
                               history_passes=history_passes)
    
    except Exception as e:
        logger.error(f'Security dashboard error: {e}')
        return render_template('security_dashboard.html', active_passes=[], history_passes=[])

@app.route('/security/action', methods=['POST'])
@login_required
@role_required('security')
def security_action():
    try:
        request_id = request.form.get('request_id')
        action = request.form.get('action')
        
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        if action == 'exit':
            c.execute('''UPDATE gate_passes 
                         SET security_action = 'exited', exit_marked_at = CURRENT_TIMESTAMP 
                         WHERE id = ?''', (request_id,))
            flash('Student marked as exited', 'success')
        elif action == 'return':
            c.execute('''UPDATE gate_passes 
                         SET security_action = 'returned', return_marked_at = CURRENT_TIMESTAMP 
                         WHERE id = ?''', (request_id,))
            flash('Student marked as returned', 'success')
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f'Security action error: {e}')
        flash('Error processing action', 'error')
    
    return redirect(url_for('security_dashboard'))

@app.route('/security/download_history')
@login_required
@role_required('security')
def download_security_history():
    """Generates and serves a CSV file of all processed gate passes for security."""
    try:
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        c.execute('''SELECT id, student_name, roll_number, reason, destination, exit_time, 
                            security_action, exit_marked_at, return_marked_at
                     FROM gate_passes 
                     WHERE security_action IS NOT NULL
                     ORDER BY id DESC''')
        data = c.fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = [
            'ID', 'Student Name', 'Roll Number', 'Reason', 'Destination', 
            'Expected Exit', 'Final Status', 'Exit Marked At', 'Return Marked At'
        ]
        writer.writerow(headers)
        
        writer.writerows(data)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=security_gate_pass_history.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    except Exception as e:
        logger.error(f'Security history download error: {e}')
        flash('Could not generate history file.', 'error')
        return redirect(url_for('security_dashboard'))


@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Fixed admin dashboard with proper data handling"""
    try:
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        # Get statistics with proper error handling
        c.execute('SELECT COUNT(*) FROM gate_passes WHERE status = "pending"')
        pending_count = (c.fetchone() or [0])[0]
            
        c.execute('SELECT COUNT(*) FROM gate_passes WHERE status = "approved"')
        approved_count = (c.fetchone() or [0])[0]
            
        c.execute('SELECT COUNT(*) FROM gate_passes WHERE status = "rejected"')
        rejected_count = (c.fetchone() or [0])[0]
            
        c.execute('SELECT COUNT(*) FROM users WHERE role = "student"')
        student_count = (c.fetchone() or [0])[0]
            
        c.execute('SELECT COUNT(*) FROM attendance WHERE percentage < 75')
        low_attendance_count = (c.fetchone() or [0])[0]
        
        # Get all users
        c.execute('''SELECT id, email, role, name, roll_number, 
                            assigned_range_start, assigned_range_end 
                     FROM users ORDER BY role, email''')
        users = c.fetchall()
        
        # Get ALL gate pass requests for history
        c.execute('''SELECT id, student_name, roll_number, reason, status, approver_email, 
                            security_action, created_at, exit_marked_at, return_marked_at
                     FROM gate_passes ORDER BY created_at DESC''')
        gate_pass_history = c.fetchall()
        
        # Get attendance data
        c.execute('''SELECT u.roll_number, u.name, COALESCE(a.percentage, 0) as attendance, 
                            a.last_updated
                     FROM users u
                     LEFT JOIN attendance a ON u.roll_number = a.roll_number
                     WHERE u.role = "student" ORDER BY u.roll_number''')
        attendance_data = c.fetchall()
        
        conn.close()
        
        logger.info(f"Admin dashboard data loaded: {student_count} students, {len(users)} total users")
        try:
            return render_template('admin_dashboard.html',
                                 pending_count=pending_count,
                                 approved_count=approved_count,
                                 rejected_count=rejected_count,
                                 student_count=student_count,
                                 low_attendance_count=low_attendance_count,
                                 users=users,
                                 gate_pass_history=gate_pass_history,
                                 attendance_data=attendance_data)
        except jinja2.exceptions.TemplateSyntaxError as e:
            trace = traceback.format_exc()
            logger.error(f'Admin dashboard TemplateSyntaxError: {e}')
            return render_template('error.html', error=str(e), trace=trace)

    except Exception as e:
        trace = traceback.format_exc()
        logger.error(f'Admin dashboard error: {e}')
        return render_template('error.html', error=str(e), trace=trace)

@app.route('/admin/download_history')
@login_required
@role_required('admin')
def download_admin_history():
    """Generates and serves a CSV file of all gate pass history for admin."""
    try:
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        c.execute('''SELECT id, student_name, roll_number, reason, status, approver_email, 
                            security_action, created_at, exit_marked_at, return_marked_at
                     FROM gate_passes ORDER BY id DESC''')
        data = c.fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = [
            'ID', 'Student Name', 'Roll Number', 'Reason', 'Approval Status', 'Approver',
            'Security Status', 'Created At', 'Exit Marked At', 'Return Marked At'
        ]
        writer.writerow(headers)
        
        writer.writerows(data)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=full_gate_pass_history.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    except Exception as e:
        logger.error(f'Admin history download error: {e}')
        flash('Could not generate history file.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_user', methods=['POST'])
@login_required
@role_required('admin')
def add_user():
    """Add new user via admin dashboard"""
    try:
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip()
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        
        if not all([email, password, role, name]):
            flash('Email, password, role and name are required', 'error')
            return redirect(url_for('admin_dashboard'))
        
        if role == 'student' and not roll_number:
            flash('Roll number is required for students', 'error')
            return redirect(url_for('admin_dashboard'))
        
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO users (email, password, role, name, roll_number) 
                     VALUES (?, ?, ?, ?, ?)''', 
                 (email, password, role, name, roll_number if role == 'student' else None))
        
        if role == 'student' and roll_number:
            c.execute('INSERT OR IGNORE INTO attendance (roll_number, percentage, uploaded_by) VALUES (?, ?, ?)',
                     (roll_number, 85.0, session['user_email']))
        
        conn.commit()
        conn.close()
        
        flash(f'{role.title()} {name} added successfully!', 'success')
        logger.info(f"User added: {email} as {role}")
        
    except sqlite3.IntegrityError:
        flash('Email already exists!', 'error')
    except Exception as e:
        logger.error(f'Add user error: {e}')
        flash('Error adding user', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/upload_attendance', methods=['POST'])
@login_required
@role_required('admin')
def upload_attendance():
    if 'attendance_file' not in request.files:
        flash('No file part in the request.', 'error')
        return redirect(url_for('admin_dashboard'))

    file = request.files['attendance_file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_dashboard'))

    if file and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file)
            
            # UPDATED CODE: Allow for either 'percentage' or 'attendance' as the column name
            if 'percentage' in df.columns:
                percentage_col = 'percentage'
            elif 'attendance' in df.columns:
                percentage_col = 'attendance'
            else:
                flash('CSV must contain a "roll_number" and either a "percentage" or "attendance" column.', 'error')
                return redirect(url_for('admin_dashboard'))

            if 'roll_number' not in df.columns:
                flash('CSV must contain a "roll_number" column.', 'error')
                return redirect(url_for('admin_dashboard'))

            conn = sqlite3.connect('gate_pass.db')
            c = conn.cursor()
            
            updated_count = 0
            for index, row in df.iterrows():
                roll_number = str(row['roll_number'])
                percentage = float(row[percentage_col]) # Use the detected column name
                
                # Using INSERT OR REPLACE to either update existing or insert new attendance record
                c.execute('''INSERT OR REPLACE INTO attendance (roll_number, percentage, uploaded_by, last_updated)
                             VALUES (?, ?, ?, CURRENT_TIMESTAMP)''', 
                          (roll_number, percentage, session['user_email']))
                updated_count += 1
            
            conn.commit()
            conn.close()
            
            flash(f'Successfully uploaded and processed {updated_count} attendance records.', 'success')
            logger.info(f"Admin {session['user_email']} uploaded attendance for {updated_count} students.")

        except Exception as e:
            logger.error(f'Error processing attendance file: {e}')
            flash(f'An error occurred while processing the file: {e}', 'error')
    else:
        flash('Invalid file format. Please upload a CSV file.', 'error')

    return redirect(url_for('admin_dashboard'))

def _get_attendance_by_roll(roll_number):
    """Helper function to get attendance data from the database."""
    try:
        conn = sqlite3.connect('gate_pass.db')
        c = conn.cursor()
        
        c.execute('''SELECT u.roll_number, u.name, u.email, 
                            COALESCE(a.percentage, 0) as attendance, 
                            a.last_updated
                     FROM users u
                     LEFT JOIN attendance a ON u.roll_number = a.roll_number
                     WHERE u.roll_number = ? AND u.role = "student"''', (roll_number,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'roll_number': result[0],
                'name': result[1],
                'email': result[2],
                'attendance': result[3],
                'last_updated': result[4] or 'Never',
            }
        else:
            return None
    except Exception as e:
        logger.error(f'Database error in _get_attendance_by_roll: {e}')
        return None

@app.route('/admin/search_attendance')
@login_required
@role_required('admin')
def search_attendance():
    roll_number = request.args.get('roll_number', '').strip()
    if not roll_number:
        return jsonify({'error': 'Roll number is required'}), 400
    
    student_data = _get_attendance_by_roll(roll_number)
    
    if student_data:
        return jsonify(student_data)
    elif student_data is None:
        return jsonify({'error': 'Student not found'}), 404
    else:
        return jsonify({'error': 'An internal error occurred'}), 500

@app.route('/approver/search_attendance')
@login_required
@role_required('approver')
def approver_search_attendance():
    roll_number = request.args.get('roll_number', '').strip()
    if not roll_number:
        return jsonify({'error': 'Roll number is required'}), 400
        
    student_data = _get_attendance_by_roll(roll_number)
    
    if student_data:
        return jsonify(student_data)
    elif student_data is None:
        return jsonify({'error': 'Student not found'}), 404
    else:
        return jsonify({'error': 'An internal error occurred'}), 500

# Template functions
@app.template_global()
def get_user_role():
    return session.get('user_role', '')

@app.template_global()
def get_user_name():
    return session.get('user_name', '')

if __name__ == '__main__':
    init_db()
    
    print("\n🛡️ CBIT Gate Pass Management System - Simplified")
    print("=" * 55)
    print("Server starting at http://localhost:5000")
    print("\n📧 WORKING Credentials:")
    print("Student 1: 232P1A3317@cbit.edu.in / 232P1A3317")
    print("Student 2: 232P1A3346@cbit.edu.in / 232P1A3346")
    print("Approver 1: approver1@cbit.edu.in / 9182302896")
    print("Approver 2: approver2@cbit.edu.in / 9876543210")  
    print("Security: security1@cbit.edu.in / 9573239692")
    print("Admin: admin1@cbit.edu.in / 6300933471")
    print("\n✅ Features:")
    print("- 2 students with attendance data")
    print("- Working admin dashboard with user management")
    print("- Sample gate pass request for testing")
    print("- Add more users via admin dashboard")
    
    app.run(debug=True, host='0.0.0.0', port=5000)