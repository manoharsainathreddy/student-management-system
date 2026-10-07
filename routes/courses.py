from flask import Blueprint, request, jsonify
from database.mongodb import get_db

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@courses_bp.route('', methods=['GET'])
def get_courses():
    try:
        db = get_db()
        courses = list(db.courses.find({}, {'_id': 0}))
        return jsonify({'success': True, 'data': courses, 'count': len(courses)}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to fetch courses: {str(e)}"}), 500

@courses_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        db = get_db()
        course = db.courses.find_one({"course_id": course_id}, {'_id': 0})
        if not course:
            return jsonify({'success': False, 'message': f"Course '{course_id}' not found"}), 404
        return jsonify({'success': True, 'data': course}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error retrieving course: {str(e)}"}), 500

@courses_bp.route('', methods=['POST'])
def create_course():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': "Invalid JSON payload"}), 400

        course_id = data.get('course_id', '').strip().upper()
        course_name = data.get('course_name', '').strip()
        credits = data.get('credits')
        department = data.get('department', '').strip()

        if not course_id or not course_name or not department:
            return jsonify({'success': False, 'message': "Course ID, Course Name, and Department are required"}), 400

        try:
            credits = int(credits)
            if credits <= 0 or credits > 10:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': "Credits must be a positive integer between 1 and 10"}), 400

        db = get_db()
        if db.courses.find_one({"course_id": course_id}):
            return jsonify({'success': False, 'message': f"Course ID '{course_id}' already exists"}), 400

        new_course = {
            "course_id": course_id,
            "course_name": course_name,
            "credits": credits,
            "department": department
        }

        db.courses.insert_one(new_course)
        new_course.pop('_id', None)
        return jsonify({'success': True, 'message': "Course added successfully", 'data': new_course}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to create course: {str(e)}"}), 500

@courses_bp.route('/<course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': "Invalid JSON payload"}), 400

        db = get_db()
        existing = db.courses.find_one({"course_id": course_id})
        if not existing:
            return jsonify({'success': False, 'message': f"Course '{course_id}' not found"}), 404

        update_fields = {}
        if 'course_name' in data and data['course_name'].strip():
            update_fields['course_name'] = data['course_name'].strip()
        if 'department' in data and data['department'].strip():
            update_fields['department'] = data['department'].strip()
        if 'credits' in data:
            try:
                cred = int(data['credits'])
                if 1 <= cred <= 10:
                    update_fields['credits'] = cred
            except (ValueError, TypeError):
                pass

        if not update_fields:
            return jsonify({'success': False, 'message': "No valid fields provided for update"}), 400

        db.courses.update_one({"course_id": course_id}, {"$set": update_fields})
        updated = db.courses.find_one({"course_id": course_id}, {'_id': 0})
        return jsonify({'success': True, 'message': "Course updated successfully", 'data': updated}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to update course: {str(e)}"}), 500

@courses_bp.route('/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        db = get_db()
        existing = db.courses.find_one({"course_id": course_id})
        if not existing:
            return jsonify({'success': False, 'message': f"Course '{course_id}' not found"}), 404

        db.courses.delete_one({"course_id": course_id})
        
        # Cascade delete related enrollments, marks, attendance
        del_enrollments = db.enrollments.delete_many({"course_id": course_id}).deleted_count
        del_marks = db.marks.delete_many({"course_id": course_id}).deleted_count
        del_attendance = db.attendance.delete_many({"course_id": course_id}).deleted_count

        return jsonify({
            'success': True,
            'message': f"Course '{course_id}' and related records deleted successfully",
            'cascaded': {
                'enrollments': del_enrollments,
                'marks': del_marks,
                'attendance': del_attendance
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to delete course: {str(e)}"}), 500
