import logging
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_client = None
_db = None

def get_client():
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
            # Test ping
            _client.admin.command('ping')
            logger.info("Successfully connected to MongoDB server.")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            _client = None
            raise Exception("MongoDB server is not running or unreachable at " + Config.MONGO_URI)
    return _client

def get_db():
    global _db
    if _db is None:
        client = get_client()
        _db = client[Config.DATABASE_NAME]
    return _db

def check_connection():
    try:
        client = get_client()
        client.admin.command('ping')
        return True, "Connected to MongoDB successfully"
    except Exception as e:
        return False, str(e)

def init_db():
    """
    Initializes database indexes for required collections.
    Does NOT drop existing collections or data.
    """
    try:
        db = get_db()
        
        # 1. Students indexes
        db.students.create_index([("student_id", ASCENDING)], unique=True, name="idx_student_id_unique")
        db.students.create_index([("email", ASCENDING)], unique=True, name="idx_student_email_unique")
        db.students.create_index([("department", ASCENDING)], name="idx_student_department")
        
        # 2. Courses indexes
        db.courses.create_index([("course_id", ASCENDING)], unique=True, name="idx_course_id_unique")
        
        # 3. Enrollments indexes
        db.enrollments.create_index(
            [("student_id", ASCENDING), ("course_id", ASCENDING), ("semester", ASCENDING)],
            unique=True,
            name="idx_enrollment_unique"
        )
        db.enrollments.create_index([("student_id", ASCENDING)], name="idx_enrollment_student_id")
        db.enrollments.create_index([("course_id", ASCENDING)], name="idx_enrollment_course_id")
        
        # 4. Marks indexes
        db.marks.create_index([("student_id", ASCENDING)], name="idx_marks_student_id")
        db.marks.create_index([("course_id", ASCENDING)], name="idx_marks_course_id")
        db.marks.create_index(
            [("student_id", ASCENDING), ("course_id", ASCENDING)],
            unique=True,
            name="idx_marks_student_course_unique"
        )
        
        # 5. Attendance indexes
        db.attendance.create_index([("student_id", ASCENDING)], name="idx_attendance_student_id")
        db.attendance.create_index([("course_id", ASCENDING)], name="idx_attendance_course_id")
        db.attendance.create_index(
            [("student_id", ASCENDING), ("course_id", ASCENDING)],
            unique=True,
            name="idx_attendance_student_course_unique"
        )
        
        logger.info("MongoDB indexes verified/created successfully.")
        return True
    except Exception as e:
        logger.error(f"Error initializing database indexes: {e}")
        return False
