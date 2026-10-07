from flask import Blueprint, jsonify
from database.mongodb import get_db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('', methods=['GET'])
def get_dashboard_stats():
    """
    Returns aggregated metrics using MongoDB aggregation pipelines.
    - Total counts (students, courses, enrollments)
    - Average marks (Aggregation $group)
    - Average attendance (Aggregation $group)
    - Students by department (Aggregation $group)
    - Grade distribution (Aggregation $group)
    - Low attendance students (<75%) (Aggregation $match + $lookup)
    """
    try:
        db = get_db()

        # 1. Total counts
        total_students = db.students.count_documents({})
        total_courses = db.courses.count_documents({})
        total_enrollments = db.enrollments.count_documents({})

        # 2. Average total marks pipeline
        avg_marks_pipeline = [
            {"$group": {"_id": None, "avg_marks": {"$avg": "$total"}}}
        ]
        avg_marks_res = list(db.marks.aggregate(avg_marks_pipeline))
        average_marks = round(avg_marks_res[0]['avg_marks'], 2) if avg_marks_res and avg_marks_res[0].get('avg_marks') is not None else 0.0

        # 3. Average attendance percentage pipeline
        avg_att_pipeline = [
            {"$group": {"_id": None, "avg_att": {"$avg": "$attendance_percentage"}}}
        ]
        avg_att_res = list(db.attendance.aggregate(avg_att_pipeline))
        average_attendance = round(avg_att_res[0]['avg_att'], 2) if avg_att_res and avg_att_res[0].get('avg_att') is not None else 0.0

        # 4. Students by department pipeline ($group)
        dept_pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        dept_raw = list(db.students.aggregate(dept_pipeline))
        students_by_department = [{"department": d['_id'] or "Unassigned", "count": d['count']} for d in dept_raw]

        # 5. Grade distribution pipeline ($group)
        grade_pipeline = [
            {"$group": {"_id": "$grade", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        grade_raw = list(db.marks.aggregate(grade_pipeline))
        grade_distribution = [{"grade": g['_id'] or "N/A", "count": g['count']} for g in grade_raw]

        # 6. Low attendance students (< 75%) pipeline ($match + $lookup)
        low_att_pipeline = [
            {"$match": {"attendance_percentage": {"$lt": 75.0}}},
            {
                "$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "student_id",
                    "as": "student"
                }
            },
            {
                "$lookup": {
                    "from": "courses",
                    "localField": "course_id",
                    "foreignField": "course_id",
                    "as": "course"
                }
            },
            {"$unwind": {"path": "$student", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$course", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "student_id": 1,
                    "student_name": "$student.name",
                    "course_id": 1,
                    "course_name": "$course.course_name",
                    "classes_held": 1,
                    "classes_attended": 1,
                    "attendance_percentage": 1
                }
            },
            {"$sort": {"attendance_percentage": 1}}
        ]
        low_attendance_students = list(db.attendance.aggregate(low_att_pipeline))

        return jsonify({
            'success': True,
            'data': {
                'total_students': total_students,
                'total_courses': total_courses,
                'total_enrollments': total_enrollments,
                'average_marks': average_marks,
                'average_attendance': average_attendance,
                'students_by_department': students_by_department,
                'grade_distribution': grade_distribution,
                'low_attendance_students': low_attendance_students
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Dashboard aggregation failed: {str(e)}"}), 500
