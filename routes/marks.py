from flask import Blueprint, request, jsonify
from database.mongodb import get_db

marks_bp = Blueprint('marks', __name__, url_prefix='/api/marks')

def calculate_grade(total):
    if total >= 90:
        return "A+"
    elif total >= 80:
        return "A"
    elif total >= 70:
        return "B+"
    elif total >= 60:
        return "B"
    elif total >= 50:
        return "C"
    elif total >= 40:
        return "D"
    else:
        return "F"

@marks_bp.route('', methods=['GET'])
def get_marks():
    try:
        db = get_db()
        student_id_filter = request.args.get('student_id', '').strip()
        course_id_filter = request.args.get('course_id', '').strip()

        query_filter = {}
        if student_id_filter:
            query_filter['student_id'] = student_id_filter
        if course_id_filter:
            query_filter['course_id'] = course_id_filter

        raw_marks = list(db.marks.find(query_filter, {'_id': 0}))

        students_dict = {s['student_id']: s['name'] for s in db.students.find({}, {'student_id': 1, 'name': 1})}
        courses_dict = {c['course_id']: c['course_name'] for c in db.courses.find({}, {'course_id': 1, 'course_name': 1})}

        enriched = []
        for item in raw_marks:
            s_name = students_dict.get(item['student_id'], 'Unknown Student')
            c_name = courses_dict.get(item['course_id'], 'Unknown Course')
            enriched.append({
                'student_id': item['student_id'],
                'student_name': s_name,
                'course_id': item['course_id'],
                'course_name': c_name,
                'internal': item.get('internal', 0),
                'external': item.get('external', 0),
                'total': item.get('total', 0),
                'grade': item.get('grade', 'F')
            })

        return jsonify({'success': True, 'data': enriched, 'count': len(enriched)}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to fetch marks: {str(e)}"}), 500

@marks_bp.route('', methods=['POST'])
def add_or_update_marks():
    """
    Creates or updates marks for a student in a course.
    Validates internal (0-30), external (0-70).
    Backend strictly calculates total and grade.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': "Invalid JSON payload"}), 400

        student_id = data.get('student_id', '').strip()
        course_id = data.get('course_id', '').strip().upper()
        internal_raw = data.get('internal')
        external_raw = data.get('external')

        if not student_id or not course_id:
            return jsonify({'success': False, 'message': "Student ID and Course ID are required"}), 400

        try:
            internal = float(internal_raw)
            external = float(external_raw)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': "Internal and External marks must be valid numbers"}), 400

        # Validate range constraints: Internal 0-30, External 0-70
        if internal < 0 or internal > 30:
            return jsonify({'success': False, 'message': "Internal marks must be between 0 and 30"}), 400
        if external < 0 or external > 70:
            return jsonify({'success': False, 'message': "External marks must be between 0 and 70"}), 400

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
        total = round(internal + external, 2)
        grade = calculate_grade(total)

        mark_doc = {
            "student_id": student_id,
            "course_id": course_id,
            "internal": internal,
            "external": external,
            "total": total,
            "grade": grade
        }

        # Upsert: if record for student_id + course_id exists, update it
        db.marks.update_one(
            {"student_id": student_id, "course_id": course_id},
            {"$set": mark_doc},
            upsert=True
        )

        return jsonify({
            'success': True,
            'message': f"Marks saved for student '{student['name']}' in '{course['course_name']}' (Total: {total}, Grade: {grade})",
            'data': mark_doc
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to save marks: {str(e)}"}), 500

@marks_bp.route('/<student_id>/<course_id>', methods=['DELETE'])
@marks_bp.route('', methods=['DELETE'])
def delete_marks(student_id=None, course_id=None):
    try:
        if not student_id:
            student_id = request.args.get('student_id', '').strip()
        if not course_id:
            course_id = request.args.get('course_id', '').strip()

        if not student_id or not course_id:
            return jsonify({'success': False, 'message': "student_id and course_id are required"}), 400

        db = get_db()
        result = db.marks.delete_one({"student_id": student_id, "course_id": course_id})
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': "Marks record not found"}), 404

        return jsonify({'success': True, 'message': "Marks record deleted successfully"}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to delete marks: {str(e)}"}), 500
