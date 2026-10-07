from flask import Blueprint, request, jsonify
from database.mongodb import get_db

enrollments_bp = Blueprint('enrollments', __name__, url_prefix='/api/enrollments')

@enrollments_bp.route('', methods=['GET'])
def get_enrollments():
    try:
        db = get_db()
        student_id_filter = request.args.get('student_id', '').strip()
        course_id_filter = request.args.get('course_id', '').strip()

        query_filter = {}
        if student_id_filter:
            query_filter['student_id'] = student_id_filter
        if course_id_filter:
            query_filter['course_id'] = course_id_filter

        raw_enrollments = list(db.enrollments.find(query_filter, {'_id': 0}))

        # Enrich with student name & course name
        students_dict = {s['student_id']: s['name'] for s in db.students.find({}, {'student_id': 1, 'name': 1})}
        courses_dict = {c['course_id']: c['course_name'] for c in db.courses.find({}, {'course_id': 1, 'course_name': 1})}

        enriched = []
        for item in raw_enrollments:
            s_name = students_dict.get(item['student_id'], 'Unknown Student')
            c_name = courses_dict.get(item['course_id'], 'Unknown Course')
            enriched.append({
                'student_id': item['student_id'],
                'student_name': s_name,
                'course_id': item['course_id'],
                'course_name': c_name,
                'semester': item.get('semester', 1)
            })

        return jsonify({'success': True, 'data': enriched, 'count': len(enriched)}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to fetch enrollments: {str(e)}"}), 500

@enrollments_bp.route('', methods=['POST'])
def create_enrollment():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': "Invalid JSON payload"}), 400

        student_id = data.get('student_id', '').strip()
        course_id = data.get('course_id', '').strip().upper()
        semester = data.get('semester')

        if not student_id or not course_id:
            return jsonify({'success': False, 'message': "Student ID and Course ID are required"}), 400

        try:
            semester = int(semester)
            if semester < 1 or semester > 10:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': "Semester must be an integer between 1 and 10"}), 400

        db = get_db()

        # 1. Verify student exists
        student = db.students.find_one({"student_id": student_id})
        if not student:
            return jsonify({'success': False, 'message': f"Student '{student_id}' does not exist"}), 404

        # 2. Verify course exists
        course = db.courses.find_one({"course_id": course_id})
        if not course:
            return jsonify({'success': False, 'message': f"Course '{course_id}' does not exist"}), 404

        # 3. Check duplicate enrollment
        existing = db.enrollments.find_one({
            "student_id": student_id,
            "course_id": course_id,
            "semester": semester
        })
        if existing:
            return jsonify({
                'success': False,
                'message': f"Student '{student_id}' is already enrolled in '{course_id}' for semester {semester}"
            }), 400

        new_enrollment = {
            "student_id": student_id,
            "course_id": course_id,
            "semester": semester
        }

        db.enrollments.insert_one(new_enrollment)
        new_enrollment.pop('_id', None)

        return jsonify({
            'success': True,
            'message': f"Enrolled student '{student['name']}' in course '{course['course_name']}' successfully",
            'data': new_enrollment
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to create enrollment: {str(e)}"}), 500

@enrollments_bp.route('', methods=['DELETE'])
def delete_enrollment():
    try:
        student_id = request.args.get('student_id', '').strip()
        course_id = request.args.get('course_id', '').strip()
        semester = request.args.get('semester')

        if not student_id or not course_id:
            return jsonify({'success': False, 'message': "student_id and course_id query parameters are required"}), 400

        query_filter = {
            "student_id": student_id,
            "course_id": course_id
        }
        if semester:
            try:
                query_filter["semester"] = int(semester)
            except ValueError:
                pass

        db = get_db()
        result = db.enrollments.delete_one(query_filter)
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': "Enrollment record not found"}), 404

        return jsonify({'success': True, 'message': "Enrollment removed successfully"}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to delete enrollment: {str(e)}"}), 500
