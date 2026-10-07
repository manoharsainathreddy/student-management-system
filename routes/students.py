import re
from flask import Blueprint, request, jsonify
from database.mongodb import get_db

students_bp = Blueprint('students', __name__, url_prefix='/api/students')

def clean_doc(doc):
    if not doc:
        return None
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

@students_bp.route('', methods=['GET'])
def get_students():
    try:
        db = get_db()
        students = list(db.students.find({}, {'_id': 0}))
        return jsonify({'success': True, 'data': students, 'count': len(students)}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to fetch students: {str(e)}"}), 500

@students_bp.route('/search', methods=['GET'])
def search_students():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return get_students()
            
        db = get_db()
        # Case-insensitive regex search across student_id, name, email, department
        regex_query = {"$regex": re.escape(query), "$options": "i"}
        search_filter = {
            "$or": [
                {"student_id": regex_query},
                {"name": regex_query},
                {"email": regex_query},
                {"department": regex_query}
            ]
        }
        students = list(db.students.find(search_filter, {'_id': 0}))
        return jsonify({'success': True, 'data': students, 'count': len(students)}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Search failed: {str(e)}"}), 500

@students_bp.route('/<student_id>', methods=['GET'])
def get_student(student_id):
    try:
        db = get_db()
        student = db.students.find_one({"student_id": student_id}, {'_id': 0})
        if not student:
            return jsonify({'success': False, 'message': f"Student '{student_id}' not found"}), 404
        return jsonify({'success': True, 'data': student}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error retrieving student: {str(e)}"}), 500

@students_bp.route('/<student_id>/full', methods=['GET'])
def get_student_full_profile(student_id):
    """
    Combines Student metadata + Enrolled Courses + Marks + Attendance.
    Crucial for detailed student profile view.
    """
    try:
        db = get_db()
        student = db.students.find_one({"student_id": student_id}, {'_id': 0})
        if not student:
            return jsonify({'success': False, 'message': f"Student '{student_id}' not found"}), 404

        # 1. Fetch enrollments & course details
        enrollments = list(db.enrollments.find({"student_id": student_id}, {'_id': 0}))
        course_ids = [e['course_id'] for e in enrollments]
        courses_dict = {
            c['course_id']: c for c in db.courses.find({"course_id": {"$in": course_ids}}, {'_id': 0})
        }
        
        enrolled_courses = []
        for e in enrollments:
            c_info = courses_dict.get(e['course_id'], {})
            enrolled_courses.append({
                'course_id': e['course_id'],
                'course_name': c_info.get('course_name', 'Unknown Course'),
                'credits': c_info.get('credits', 0),
                'semester': e.get('semester', student.get('semester', 1))
            })

        # 2. Fetch marks
        raw_marks = list(db.marks.find({"student_id": student_id}, {'_id': 0}))
        marks = []
        for m in raw_marks:
            c_info = courses_dict.get(m['course_id'], {})
            marks.append({
                'course_id': m['course_id'],
                'course_name': c_info.get('course_name', m['course_id']),
                'internal': m.get('internal', 0),
                'external': m.get('external', 0),
                'total': m.get('total', 0),
                'grade': m.get('grade', 'N/A')
            })

        # 3. Fetch attendance
        raw_attendance = list(db.attendance.find({"student_id": student_id}, {'_id': 0}))
        attendance = []
        for a in raw_attendance:
            c_info = courses_dict.get(a['course_id'], {})
            attendance.append({
                'course_id': a['course_id'],
                'course_name': c_info.get('course_name', a['course_id']),
                'classes_held': a.get('classes_held', 0),
                'classes_attended': a.get('classes_attended', 0),
                'attendance_percentage': a.get('attendance_percentage', 0.0)
            })

        return jsonify({
            'success': True,
            'data': {
                'student': student,
                'enrollments': enrolled_courses,
                'marks': marks,
                'attendance': attendance
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error loading profile: {str(e)}"}), 500

@students_bp.route('', methods=['POST'])
def create_student():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': "Invalid JSON payload"}), 400

        student_id = data.get('student_id', '').strip()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        department = data.get('department', '').strip()
        year = data.get('year')
        semester = data.get('semester')

        # Validation
        if not student_id or not name or not email or not phone or not department:
            return jsonify({'success': False, 'message': "All fields (student_id, name, email, phone, department) are required"}), 400

        try:
            year = int(year)
            semester = int(semester)
            if year < 1 or year > 5 or semester < 1 or semester > 10:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': "Year must be 1-5 and Semester must be 1-10"}), 400

        db = get_db()
        
        # Check duplicate student_id
        if db.students.find_one({"student_id": student_id}):
            return jsonify({'success': False, 'message': f"Student ID '{student_id}' already exists"}), 400

        # Check duplicate email
        if db.students.find_one({"email": email}):
            return jsonify({'success': False, 'message': f"Email '{email}' is already registered"}), 400

        new_student = {
            "student_id": student_id,
            "name": name,
            "email": email,
            "phone": phone,
            "department": department,
            "year": year,
            "semester": semester
        }

        db.students.insert_one(new_student)
        new_student.pop('_id', None)
        return jsonify({'success': True, 'message': "Student added successfully", 'data': new_student}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to create student: {str(e)}"}), 500

@students_bp.route('/<student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': "Invalid JSON payload"}), 400

        db = get_db()
        existing = db.students.find_one({"student_id": student_id})
        if not existing:
            return jsonify({'success': False, 'message': f"Student '{student_id}' not found"}), 404

        update_fields = {}
        if 'name' in data and data['name'].strip():
            update_fields['name'] = data['name'].strip()
        if 'email' in data and data['email'].strip():
            new_email = data['email'].strip().lower()
            # check email collision
            email_owner = db.students.find_one({"email": new_email})
            if email_owner and email_owner['student_id'] != student_id:
                return jsonify({'success': False, 'message': f"Email '{new_email}' is used by another student"}), 400
            update_fields['email'] = new_email
        if 'phone' in data and data['phone'].strip():
            update_fields['phone'] = data['phone'].strip()
        if 'department' in data and data['department'].strip():
            update_fields['department'] = data['department'].strip()
        if 'year' in data:
            try:
                yr = int(data['year'])
                if 1 <= yr <= 5:
                    update_fields['year'] = yr
            except (ValueError, TypeError):
                pass
        if 'semester' in data:
            try:
                sem = int(data['semester'])
                if 1 <= sem <= 10:
                    update_fields['semester'] = sem
            except (ValueError, TypeError):
                pass

        if not update_fields:
            return jsonify({'success': False, 'message': "No valid fields provided for update"}), 400

        db.students.update_one({"student_id": student_id}, {"$set": update_fields})
        updated = db.students.find_one({"student_id": student_id}, {'_id': 0})
        return jsonify({'success': True, 'message': "Student updated successfully", 'data': updated}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to update student: {str(e)}"}), 500

@students_bp.route('/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """
    Deletes student and implements cascading deletion of related:
    - enrollments
    - marks
    - attendance
    """
    try:
        db = get_db()
        existing = db.students.find_one({"student_id": student_id})
        if not existing:
            return jsonify({'success': False, 'message': f"Student '{student_id}' not found"}), 404

        # Delete from students collection
        db.students.delete_one({"student_id": student_id})
        
        # Cascade delete related collections
        del_enrollments = db.enrollments.delete_many({"student_id": student_id}).deleted_count
        del_marks = db.marks.delete_many({"student_id": student_id}).deleted_count
        del_attendance = db.attendance.delete_many({"student_id": student_id}).deleted_count

        return jsonify({
            'success': True,
            'message': f"Student '{student_id}' and related records deleted successfully",
            'cascaded': {
                'enrollments': del_enrollments,
                'marks': del_marks,
                'attendance': del_attendance
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to delete student: {str(e)}"}), 500
