⚙️ Technology Stack
Backend: Python Flask
Database: SQLite (local file) with attendance table
Frontend: HTML, CSS, JavaScript
File Processing: Pandas (CSV/Excel), PyPDF2 (PDF support)
Email: SMTP (Gmail/SendGrid compatible)
Authentication: Session-based with role-specific password handling
📊 Attendance Management Features
For Admin
Upload Attendance: CSV/Excel file upload with automatic processing
Search Students: Quick search by roll number with full details
Monitor Low Attendance: Dashboard shows count of students below 75%
File Format Support: CSV, Excel (.xlsx, .xls) files accepted
Bulk Updates: Update all student attendance records at once
For Approvers
Real-time Visibility: See attendance percentage when reviewing requests
Visual Warnings: Red flags for students with <75% attendance
Email Alerts: Attendance information included in notification emails
Decision Support: Make informed approval decisions
For Students
Attendance Display: See your current attendance on dashboard
Warning System: Visual alerts if attendance is below 75%
Transparent Process: Know that approvers will see attendance data
📁 Enhanced Project Structure
gate_pass_system/
├── app.py                    # Main Flask application with attendance
├── requirements.txt          # Updated Python dependencies
├── gate_pass.db             # SQLite database (auto-created)
├── uploads/                 # Attendance file uploads directory
├── sample_attendance.csv    # Sample CSV for testing
├── templates/               # HTML templates
│   ├── login.html
│   ├── student_dashboard.html    # With attendance display
│   ├── approver_dashboard.html   # With attendance columns
│   ├── security_dashboard.html
│   └── admin_dashboard.html      # With attendance management
└── README.md
🔧 New API Endpoints
Attendance Management
POST /admin/upload_attendance - Upload CSV/Excel attendance files
GET /admin/search_attendance - Search student attendance by roll number
📋 Attendance File Format
CSV Format Example:
csv
roll_number,attendance
232P1A3301,85.5
232P1A3302,72.3
232P1A3303,91.2
Excel Format:
Same columns in Excel format (.xlsx or .xls files)

Required Columns:
roll_number: Student roll number (e.g., 232P1A3301)
attendance or percentage: Attendance percentage (0-100)
🚀 Quick Setup with Attendance
Prerequisites
Python 3.7+
pip package manager
Installation
Install enhanced dependencies
bash
pip install Flask==2.3.3 pandas==1.5.3 openpyxl==3.0.10 PyPDF2==3.0.1
Run the updated application
bash
python app.py
Test attendance features
Login as admin: admin1@cbit.edu.in / 6300933471
Upload the sample CSV file provided
Search for student attendance
Login as approver to see attendance in requests
📈 Usage Workflows
Admin Attendance Management
Login as admin
Go to "Attendance" tab
Upload CSV/Excel file with attendance data
Search specific students by roll number
Monitor low attendance students in dashboard
Approver Review Process
Login as approver
View pending requests with attendance columns
See red warning for students with <75% attendance
Make informed approval/rejection decisions
Receive email notifications with attendance info
Student Request Process
Login as student
See your attendance percentage on dashboard
Get warning if attendance is below 75%
Submit gate pass request knowing approver will see attendance
Receive email notification about approval/rejection
🛠️ Database Schema Updates
New Attendance Table
sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT UNIQUE NOT NULL,
    percentage REAL NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT,
    FOREIGN KEY (roll_number) REFERENCES users(roll_number)
);
🔍 Troubleshooting Attendance Features
File Upload Issues
Ensure CSV/Excel has required columns: roll_number, attendance
Check file size (16MB max)
Verify roll numbers match student records
Attendance Not Showing
Upload attendance data via admin panel
Check if roll numbers match exactly
Refresh browser after upload
Search Not Working
Enter exact roll number (e.g., 232P1A3301)
Ensure student exists in system
Check network connection for AJAX requests
🎯 Key Improvements
✅ Fixed Student Login Issue: Students now use plain text passwords (roll numbers)
📊 Added Attendance System: Complete CSV/Excel upload and management
⚠️ Visual Warnings: Red flags for low attendance students
🔍 Search Functionality: Admin can quickly find student attendance
📧 Enhanced Emails: Attendance info included in notifications
📱 Better UI: Attendance columns and visual indicators
📞 Support & Customization
For technical support or feature requests:

Attendance file format issues
Integration with existing student management systems
Custom attendance thresholds
Additional reporting features
🛡️ Built for CBIT and similar educational institutions to modernize gate pass management with integrated attendance monitoring for enhanced academic oversight.# 🎓 College Gate Pass Management System

A comprehensive web application for managing digital gate passes in educational institutions, eliminating the need for handwritten passes and providing secure, trackable access control.

🎯 Features
🔐 Multi-Role Authentication
Students: Request gate passes with institutional email
Approvers (Faculty): Review and approve/reject requests
Security: Monitor exits and returns
Admin: Complete system management
📱 Role-Based Dashboards
Student Dashboard: Submit requests, track status, view history
Approver Dashboard: Manage pending requests, add remarks
Security Dashboard: View approved passes, mark exits/returns
Admin Dashboard: User management, assignments, reports
📧 Email Notifications
Automatic notifications when requests are submitted
Status updates sent to students upon approval/rejection
Real-time communication between all stakeholders
🛡️ Security Features
Prevents fake handwritten passes
Digital approval workflow
Trackable exit/return system
Secure role-based access control
🚀 Quick Setup
Prerequisites
Python 3.7+
pip package manager
Installation
Clone/Download the project files
bash
mkdir gate_pass_system
cd gate_pass_system
Create the following files in your project directory:
app.py (Main Flask application)
requirements.txt (Python dependencies)
Create a templates/ folder and add:
login.html
student_dashboard.html
approver_dashboard.html
security_dashboard.html
admin_dashboard.html
Install dependencies
bash
pip install -r requirements.txt
Configure Email (Optional)
Open app.py
Update email configuration:
python
EMAIL_ADDRESS = 'your-email@gmail.com'
EMAIL_PASSWORD = 'your-app-password'  # Use App Password for Gmail
Run the application
bash
python app.py
Access the system
Open your browser and go to: http://localhost:5000
Use the demo credentials below to login
🔑 Demo Credentials
Students
Email: 232P1A3301@cbit.edu.in | Password: 232P1A3301
Email: 232P1A3361@cbit.edu.in | Password: 232P1A3361
Faculty (Approver)
Email: approver1@cbit.edu.in | Password: 9182302896
Name: Mr. Krupasagar
Assigned Students: 232P1A3301 – 232P1A3330
Security Staff
Email: security1@cbit.edu.in | Password: 9573239692
Admin
Email: admin1@cbit.edu.in | Password: 6300933471
📋 User Workflows
For Students
Login with institutional email
Fill out gate pass request form
Receive email notification when approved/rejected
Track request status in dashboard
For Approvers
Login to view pending requests
Review student details and request reason
Approve/reject with remarks
Student receives automatic notification
For Security
View only approved gate passes
Mark students as "Exited" when leaving
Mark students as "Returned" when coming back
Real-time dashboard updates
For Admin
Manage all user accounts
Assign student ranges to approvers
View system reports and statistics
Add new users to the system
🛠️ Technology Stack
Backend: Python Flask
Database: SQLite (local file)
Frontend: HTML, CSS, JavaScript
Email: SMTP (Gmail/SendGrid compatible)
Authentication: Session-based
📁 Project Structure
gate_pass_system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── gate_pass.db          # SQLite database (auto-created)
├── templates/            # HTML templates
│   ├── login.html
│   ├── student_dashboard.html
│   ├── approver_dashboard.html
│   ├── security_dashboard.html
│   └── admin_dashboard.html
└── README.md
⚙️ Configuration
Database
SQLite database is automatically created on first run
Default users are inserted automatically
Data persists between application restarts
Email Setup (Gmail)
Enable 2-Factor Authentication on your Gmail account
Generate an App Password: Google App Passwords
Update EMAIL_ADDRESS and EMAIL_PASSWORD in app.py
Customization
Update college name and branding in templates
Modify default users in init_db() function
Adjust student roll number patterns as needed
🔧 Advanced Features
Admin Functions
User Management: Add/remove users, bulk add students, reset passwords
Assignment Management: Assign student roll number ranges to specific approvers
Bulk Operations: Add students in ranges (e.g., 232P1A3401 to 232P1A3450)
Reporting: View statistics and generate reports
System Monitoring: Track all gate pass activities
Flexible Assignments: Admin can reassign student ranges to different approvers anytime
Security Features
Session-based authentication
Role-based access control
Input validation and sanitization
CSRF protection ready (can be enhanced)
🐛 Troubleshooting
Common Issues
Database not found
Ensure app.py is running from the correct directory
Database file gate_pass.db should be created automatically
Email not sending
Check email credentials in app.py
Verify Gmail App Password setup
Check firewall/antivirus settings
Login issues
Use exact email addresses from demo credentials
Passwords are case-sensitive
Clear browser cache if needed
Port already in use
Change port in app.py: app.run(port=5001)
Or kill existing Flask processes
📝 Development Notes
Database Schema
users: Stores all user accounts with roles and assignments
gate_passes: Stores all gate pass requests with status tracking
Security Considerations
In production, use proper password hashing (bcrypt)
Implement HTTPS for secure communication
Add rate limiting for login attempts
Use environment variables for sensitive configuration
Scalability
Can be easily migrated to PostgreSQL/MySQL
Redis can be added for session management
Docker containerization ready
🤝 Contributing
Fork the repository
Create a feature branch
Make your changes
Test thoroughly
Submit a pull request
📞 Support
For technical support or customization requests:

Create an issue in the repository
Provide detailed error messages and system information
Include steps to reproduce any problems
📄 License
This project is available for educational and institutional use. Please customize branding and credentials before production deployment.

🎓 Built for CBIT and similar educational institutions to modernize gate pass management and enhance campus security.

