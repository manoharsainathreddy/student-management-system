import os
import logging
from flask import Flask, render_template, jsonify
from config import Config
from database.mongodb import init_db, check_connection
from routes.students import students_bp
from routes.courses import courses_bp
from routes.enrollments import enrollments_bp
from routes.marks import marks_bp
from routes.attendance import attendance_bp
from routes.dashboard import dashboard_bp
from routes.auth import auth_bp
from routes.results import results_bp
from routes.reports import reports_bp
from routes.admin import admin_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Register API Blueprints
app.register_blueprint(students_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(enrollments_bp)
app.register_blueprint(marks_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(results_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(admin_bp)

# All 9 Screen HTML Page Routes
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/students')
def students_page():
    return render_template('students.html')

@app.route('/courses')
def courses_page():
    return render_template('courses.html')

@app.route('/enrollments')
def enrollments_page():
    return render_template('enrollments.html')

@app.route('/attendance')
def attendance_page():
    return render_template('attendance.html')

@app.route('/marks')
def marks_page():
    return render_template('marks.html')

@app.route('/results')
def results_page():
    return render_template('results.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

@app.route('/collections')
def collections_page():
    return render_template('collections.html')

# Health Check & DB Status Endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    connected, message = check_connection()
    status_code = 200 if connected else 500
    return jsonify({
        'status': 'healthy' if connected else 'unhealthy',
        'mongodb_connected': connected,
        'message': message,
        'database': Config.DATABASE_NAME
    }), status_code

# Custom Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'success': False, 'message': 'Resource or endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# Initialize DB Indexes on Application Startup
with app.app_context():
    try:
        init_db()
    except Exception as e:
        logger.warning(f"Could not auto-initialize DB indexes on startup: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print(" [+] Starting Student Management System (MongoDB + Flask) ")
    print(f" [*] URL: http://127.0.0.1:{port}")
    print(f" [*] Database: {Config.DATABASE_NAME}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
