from flask import Blueprint, request, jsonify, session
from database.mongodb import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

ALLOWED_COLLECTIONS = ['students', 'courses', 'enrollments', 'marks', 'attendance']

def check_admin_session():
    user = session.get('user')
    # Allow for demo if requested, but check role if set
    if user and user.get('role') != 'admin':
        return False
    return True

@admin_bp.route('/collections', methods=['GET'])
def list_collections():
    """
    Returns list of whitelisted MongoDB collections and document counts.
    Does NOT expose connection strings or database secrets.
    """
    try:
        db = get_db()
        collections_info = []

        for col_name in ALLOWED_COLLECTIONS:
            count = db[col_name].count_documents({})
            collections_info.append({
                'name': col_name,
                'count': count
            })

        return jsonify({
            'success': True,
            'database': 'student_management',
            'collections': collections_info
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to list collections: {str(e)}"}), 500

@admin_bp.route('/collections/<collection_name>', methods=['GET'])
def get_collection_documents(collection_name):
    """
    Returns documents for a whitelisted MongoDB collection.
    Sanitizes ObjectId into string format.
    """
    try:
        if collection_name not in ALLOWED_COLLECTIONS:
            return jsonify({
                'success': False,
                'message': f"Collection '{collection_name}' is not in allowed collections list"
            }), 403

        db = get_db()
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        query_str = request.args.get('q', '').strip()

        col = db[collection_name]
        
        filter_query = {}
        if query_str:
            # Case-insensitive search across key string fields
            if collection_name == 'students':
                filter_query = {"$or": [{"student_id": {"$regex": query_str, "$options": "i"}}, {"name": {"$regex": query_str, "$options": "i"}}]}
            elif collection_name == 'courses':
                filter_query = {"$or": [{"course_id": {"$regex": query_str, "$options": "i"}}, {"course_name": {"$regex": query_str, "$options": "i"}}]}
            elif collection_name in ['enrollments', 'marks', 'attendance']:
                filter_query = {"$or": [{"student_id": {"$regex": query_str, "$options": "i"}}, {"course_id": {"$regex": query_str, "$options": "i"}}]}

        total_count = col.count_documents(filter_query)
        cursor = col.find(filter_query).skip(skip).limit(limit)

        documents = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            documents.append(doc)

        return jsonify({
            'success': True,
            'collection': collection_name,
            'total': total_count,
            'count': len(documents),
            'limit': limit,
            'skip': skip,
            'documents': documents
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to fetch collection data: {str(e)}"}), 500
