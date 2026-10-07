from flask import Blueprint, request, jsonify
from database.mongodb import get_db

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@attendance_bp.route('', methods=['GET'])
def get_attendance():
    try:
        db = get_db()
        student_id_filter = request.args.get('student_id', '').strip()
        course_id_filter = request.args.get('course_id', '').strip()

        query_filter = {}
        if student_id_filter:
            query_filter['student_id'] = student_id_filter
        if course_id_filter:
            query_filter['course_id'] = course_id_filter

        raw_attendance = list(db.attendance.find(query_filter, {'_id': 0}))

        students_dict = {s['student_id']: s['name'] for s in db.students.find({}, {'student_id': 1, 'name': 1})}
        courses_dict = {c['course_id']: c['course_name'] for c in db.courses.find({}, {'course_id': 1, 'course_name': 1})}

        enriched = []
        for item in raw_attendance:
            s_name = students_dict.get(item['student_id'], 'Unknown Student')
            c_name = courses_dict.get(item['course_id'], 'Unknown Course')
            pct = item.get('attendance_percentage', 0.0)
            enriched.append({
                'student_id': item['student_id'],
                'student_name': s_name,
                'course_id': item['course_id'],
                'course_name': c_name,
                'classes_held': item.get('classes_held', 0),
                'classes_attended': item.get('classes_attended', 0),
                'attendance_percentage': pct,
                'is_low_attendance': pct < 75.0
            })

        return jsonify({'success': True, 'data': enriched, 'count': len(enriched)}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to fetch attendance: {str(e)}"}), 500

@attendance_bp.route('', methods=['POST'])
def add_or_update_attendance():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': "Invalid JSON payload"}), 400

        student_id = data.get('student_id', '').strip()
        course_id = data.get('course_id', '').strip().upper()
        classes_held_raw = data.get('classes_held')
        classes_attended_raw = data.get('classes_attended')

        if not student_id or not course_id:
            return jsonify({'success': False, 'message': "Student ID and Course ID are required"}), 400

        try:
            classes_held = int(classes_held_raw)
            classes_attended = int(classes_attended_raw)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': "Classes held and attended must be integers"}), 400

        # Validations
        if classes_held <= 0:
            return jsonify({'success': False, 'message': "Classes held must be greater than 0"}), 400
        if classes_attended < 0:
            return jsonify({'success': False, 'message': "Classes attended cannot be negative"}), 400
        if classes_attended > classes_held:
            return jsonify({
                'success': False,
                'message': f"Classes attended ({classes_attended}) cannot exceed total classes held ({classes_held})"
            }), 400

        db = get_db()

        # Check student exists
        student = db.students.find_one({"student_id": student_id})
        if not student:
            return jsonify({'success': False, 'message': f"Student '{student_id}' does not exist"}), 404

        # Check course exists
        course = db.courses.find_one({"course_id": course_id})
        if not course:
            return jsonify({'success': False, 'message': f"Course '{course_id}' does not exist"}), 404

        # Backend calculation
        percentage = round((classes_attended / classes_held) * 100, 2)

        attendance_doc = {
            "student_id": student_id,
            "course_id": course_id,
            "classes_held": classes_held,
            "classes_attended": classes_attended,
            "attendance_percentage": percentage
        }

        db.attendance.update_one(
            {"student_id": student_id, "course_id": course_id},
            {"$set": attendance_doc},
            upsert=True
        )

        return jsonify({
            'success': True,
            'message': f"Attendance recorded for '{student['name']}' in '{course['course_name']}': {percentage}%",
            'data': attendance_doc
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to save attendance: {str(e)}"}), 500

@attendance_bp.route('/<student_id>/<course_id>', methods=['DELETE'])
@attendance_bp.route('', methods=['DELETE'])
def delete_attendance(student_id=None, course_id=None):
    try:
        if not student_id:
            student_id = request.args.get('student_id', '').strip()
        if not course_id:
            course_id = request.args.get('course_id', '').strip()

        if not student_id or not course_id:
            return jsonify({'success': False, 'message': "student_id and course_id are required"}), 400

        db = get_db()
        result = db.attendance.delete_one({"student_id": student_id, "course_id": course_id})
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': "Attendance record not found"}), 404

        return jsonify({'success': True, 'message': "Attendance record deleted successfully"}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to delete attendance: {str(e)}"}), 500
