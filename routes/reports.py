from flask import Blueprint, request, jsonify
from database.mongodb import get_db

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@reports_bp.route('/attendance-shortage', methods=['GET'])
def get_attendance_shortage():
    """
    Report A: Attendance Shortage Report
    Filters students whose attendance is below configurable threshold (default 75%).
    Uses MongoDB $match + $lookup aggregation pipeline.
    """
    try:
        threshold_str = request.args.get('threshold', '75.0').strip()
        try:
            threshold = float(threshold_str)
        except ValueError:
            threshold = 75.0

        db = get_db()
        pipeline = [
            {"$match": {"attendance_percentage": {"$lt": threshold}}},
            {
                "$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "student_id",
                    "as": "student_info"
                }
            },
            {
                "$lookup": {
                    "from": "courses",
                    "localField": "course_id",
                    "foreignField": "course_id",
                    "as": "course_info"
                }
            },
            {"$unwind": {"path": "$student_info", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$course_info", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "student_id": 1,
                    "student_name": "$student_info.name",
                    "department": "$student_info.department",
                    "course_id": 1,
                    "course_name": "$course_info.course_name",
                    "classes_held": 1,
                    "classes_attended": 1,
                    "attendance_percentage": 1,
                    "threshold_applied": {"$literal": threshold},
                    "status": {"$literal": "SHORTAGE"}
                }
            },
            {"$sort": {"attendance_percentage": 1}}
        ]

        shortage_records = list(db.attendance.aggregate(pipeline))

        return jsonify({
            'success': True,
            'threshold': threshold,
            'count': len(shortage_records),
            'data': shortage_records
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to generate shortage report: {str(e)}"}), 500

@reports_bp.route('/grade-distribution', methods=['GET'])
def get_grade_distribution():
    """
    Report B: Grade Distribution Report
    Summarizes grade counts and computes overall pass/fail analytics using MongoDB $group.
    """
    try:
        db = get_db()
        pipeline = [
            {"$group": {"_id": "$grade", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        raw_grades = list(db.marks.aggregate(pipeline))

        # Standard grade categories
        all_grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'D', 'F']
        grade_map = {g: 0 for g in all_grades}

        total_records = 0
        fail_count = 0

        for item in raw_grades:
            g_name = item['_id']
            cnt = item['count']
            if g_name in grade_map:
                grade_map[g_name] += cnt
            else:
                grade_map[g_name] = cnt
            
            total_records += cnt
            if g_name == 'F':
                fail_count += cnt

        pass_count = total_records - fail_count
        pass_percentage = round((pass_count / total_records) * 100, 2) if total_records > 0 else 0.0

        distribution_list = [{"grade": g, "count": grade_map.get(g, 0)} for g in all_grades]

        return jsonify({
            'success': True,
            'data': {
                'distribution': distribution_list,
                'summary': {
                    'total_evaluations': total_records,
                    'pass_count': pass_count,
                    'fail_count': fail_count,
                    'pass_percentage': pass_percentage
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to generate grade distribution report: {str(e)}"}), 500
