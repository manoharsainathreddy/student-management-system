from flask import Blueprint, request, jsonify
from database.mongodb import get_db

results_bp = Blueprint('results', __name__, url_prefix='/api/results')

GRADE_POINTS = {
    'A+': 10,
    'A': 9,
    'B+': 8,
    'B': 7,
    'C': 6,
    'D': 5,
    'F': 0
}

@results_bp.route('/<student_id>', methods=['GET'])
def get_student_results(student_id):
    """
    Computes mark sheet & SGPA for a given student based on MongoDB collections.
    Formula: SGPA = Sum(Credits * GradePoint) / Sum(Credits)
    """
    try:
        db = get_db()
        student = db.students.find_one({"student_id": student_id}, {'_id': 0})
        if not student:
            return jsonify({'success': False, 'message': f"Student '{student_id}' not found"}), 404

        # 1. Fetch enrollments & course metadata
        enrollments = list(db.enrollments.find({"student_id": student_id}, {'_id': 0}))
        course_ids = [e['course_id'] for e in enrollments]
        courses_dict = {
            c['course_id']: c for c in db.courses.find({"course_id": {"$in": course_ids}}, {'_id': 0})
        }

        # 2. Fetch marks
        marks_dict = {
            m['course_id']: m for m in db.marks.find({"student_id": student_id}, {'_id': 0})
        }

        course_results = []
        total_credits = 0
        total_credit_points = 0.0

        for e in enrollments:
            cid = e['course_id']
            c_info = courses_dict.get(cid, {})
            m_info = marks_dict.get(cid, {})

            credits = c_info.get('credits', 4)
            internal = m_info.get('internal', 0.0)
            external = m_info.get('external', 0.0)
            total_marks = m_info.get('total', 0.0)
            grade = m_info.get('grade', 'F')
            gp = GRADE_POINTS.get(grade, 0)

            credit_point_earned = credits * gp

            total_credits += credits
            total_credit_points += credit_point_earned

            course_results.append({
                'course_id': cid,
                'course_name': c_info.get('course_name', cid),
                'credits': credits,
                'internal': internal,
                'external': external,
                'total_marks': total_marks,
                'grade': grade,
                'grade_point': gp,
                'credit_points_earned': credit_point_earned
            })

        sgpa = round(total_credit_points / total_credits, 2) if total_credits > 0 else 0.0

        # Class determination based on SGPA
        if sgpa >= 8.5:
            academic_status = "First Class with Distinction"
        elif sgpa >= 7.0:
            academic_status = "First Class"
        elif sgpa >= 6.0:
            academic_status = "Second Class"
        elif sgpa >= 5.0:
            academic_status = "Pass Class"
        else:
            academic_status = "Needs Improvement"

        return jsonify({
            'success': True,
            'data': {
                'student': student,
                'courses': course_results,
                'summary': {
                    'total_courses': len(course_results),
                    'total_credits': total_credits,
                    'total_credit_points': total_credit_points,
                    'sgpa': sgpa,
                    'academic_status': academic_status
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to compute results: {str(e)}"}), 500
