import os
import sys

# Ensure root folder is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.mongodb import get_db, init_db, check_connection
from routes.marks import calculate_grade

def seed_sample_data():
    """
    Seeds realistic sample data for Students, Courses, Enrollments, Marks, and Attendance.
    Prevents duplicate insertions.
    """
    connected, msg = check_connection()
    if not connected:
        print(f"[ERROR] Cannot seed data: MongoDB connection failed ({msg})")
        return False

    init_db()
    db = get_db()
    print("[+] Seeding realistic sample data into MongoDB database 'student_management'...")

    # 1. SAMPLE STUDENTS
    students = [
        {
            "student_id": "STU001",
            "name": "Rahul Kumar",
            "email": "rahul@gmail.com",
            "phone": "9876543210",
            "department": "Computer Science",
            "year": 2,
            "semester": 4
        },
        {
            "student_id": "STU002",
            "name": "Priya Sharma",
            "email": "priya.sharma@gmail.com",
            "phone": "9876543211",
            "department": "Computer Science",
            "year": 2,
            "semester": 4
        },
        {
            "student_id": "STU003",
            "name": "Amit Patel",
            "email": "amit.patel@gmail.com",
            "phone": "9876543212",
            "department": "Electronics",
            "year": 3,
            "semester": 6
        },
        {
            "student_id": "STU004",
            "name": "Sneha Reddy",
            "email": "sneha.reddy@gmail.com",
            "phone": "9876543213",
            "department": "Electronics",
            "year": 3,
            "semester": 6
        },
        {
            "student_id": "STU005",
            "name": "Vikram Singh",
            "email": "vikram.singh@gmail.com",
            "phone": "9876543214",
            "department": "Mechanical",
            "year": 1,
            "semester": 2
        },
        {
            "student_id": "STU006",
            "name": "Ananya Roy",
            "email": "ananya.roy@gmail.com",
            "phone": "9876543215",
            "department": "Computer Science",
            "year": 4,
            "semester": 8
        },
        {
            "student_id": "STU007",
            "name": "Rohan Verma",
            "email": "rohan.verma@gmail.com",
            "phone": "9876543216",
            "department": "Civil Engineering",
            "year": 2,
            "semester": 4
        },
        {
            "student_id": "STU008",
            "name": "Kavya Nair",
            "email": "kavya.nair@gmail.com",
            "phone": "9876543217",
            "department": "Information Technology",
            "year": 3,
            "semester": 5
        }
    ]

    inserted_students = 0
    for s in students:
        res = db.students.update_one({"student_id": s["student_id"]}, {"$set": s}, upsert=True)
        if res.upserted_id:
            inserted_students += 1
    print(f"  [OK] Students: {inserted_students} new added, {len(students)} total verified.")

    # 2. SAMPLE COURSES
    courses = [
        {
            "course_id": "CS101",
            "course_name": "Database Management Systems",
            "credits": 4,
            "department": "Computer Science"
        },
        {
            "course_id": "CS102",
            "course_name": "Data Structures & Algorithms",
            "credits": 4,
            "department": "Computer Science"
        },
        {
            "course_id": "CS103",
            "course_name": "Operating Systems",
            "credits": 3,
            "department": "Computer Science"
        },
        {
            "course_id": "EC101",
            "course_name": "Digital Electronics",
            "credits": 4,
            "department": "Electronics"
        },
        {
            "course_id": "MA101",
            "course_name": "Applied Mathematics & Calculus",
            "credits": 4,
            "department": "Mathematics"
        }
    ]

    inserted_courses = 0
    for c in courses:
        res = db.courses.update_one({"course_id": c["course_id"]}, {"$set": c}, upsert=True)
        if res.upserted_id:
            inserted_courses += 1
    print(f"  [OK] Courses: {inserted_courses} new added, {len(courses)} total verified.")

    # 3. SAMPLE ENROLLMENTS
    enrollments = [
        {"student_id": "STU001", "course_id": "CS101", "semester": 4},
        {"student_id": "STU001", "course_id": "CS102", "semester": 4},
        {"student_id": "STU001", "course_id": "CS103", "semester": 4},
        {"student_id": "STU002", "course_id": "CS101", "semester": 4},
        {"student_id": "STU002", "course_id": "CS102", "semester": 4},
        {"student_id": "STU003", "course_id": "EC101", "semester": 6},
        {"student_id": "STU003", "course_id": "MA101", "semester": 6},
        {"student_id": "STU004", "course_id": "EC101", "semester": 6},
        {"student_id": "STU005", "course_id": "MA101", "semester": 2},
        {"student_id": "STU005", "course_id": "CS101", "semester": 2},
        {"student_id": "STU006", "course_id": "CS103", "semester": 8},
        {"student_id": "STU007", "course_id": "MA101", "semester": 4},
        {"student_id": "STU008", "course_id": "CS102", "semester": 5}
    ]

    inserted_enrollments = 0
    for e in enrollments:
        res = db.enrollments.update_one(
            {"student_id": e["student_id"], "course_id": e["course_id"], "semester": e["semester"]},
            {"$set": e},
            upsert=True
        )
        if res.upserted_id:
            inserted_enrollments += 1
    print(f"  [OK] Enrollments: {inserted_enrollments} new added, {len(enrollments)} total verified.")

    # 4. SAMPLE MARKS
    raw_marks = [
        {"student_id": "STU001", "course_id": "CS101", "internal": 28, "external": 68}, # 96 -> A+
        {"student_id": "STU001", "course_id": "CS102", "internal": 25, "external": 60}, # 85 -> A
        {"student_id": "STU001", "course_id": "CS103", "internal": 22, "external": 56}, # 78 -> B+
        {"student_id": "STU002", "course_id": "CS101", "internal": 27, "external": 65}, # 92 -> A+
        {"student_id": "STU002", "course_id": "CS102", "internal": 20, "external": 45}, # 65 -> B
        {"student_id": "STU003", "course_id": "EC101", "internal": 24, "external": 58}, # 82 -> A
        {"student_id": "STU003", "course_id": "MA101", "internal": 18, "external": 38}, # 56 -> C
        {"student_id": "STU004", "course_id": "EC101", "internal": 29, "external": 67}, # 96 -> A+
        {"student_id": "STU005", "course_id": "MA101", "internal": 12, "external": 25}, # 37 -> F
        {"student_id": "STU005", "course_id": "CS101", "internal": 15, "external": 32}, # 47 -> D
        {"student_id": "STU006", "course_id": "CS103", "internal": 26, "external": 62}, # 88 -> A
        {"student_id": "STU007", "course_id": "MA101", "internal": 21, "external": 52}, # 73 -> B+
        {"student_id": "STU008", "course_id": "CS102", "internal": 23, "external": 55}  # 78 -> B+
    ]

    inserted_marks = 0
    for m in raw_marks:
        total = round(m["internal"] + m["external"], 2)
        grade = calculate_grade(total)
        mark_doc = {
            "student_id": m["student_id"],
            "course_id": m["course_id"],
            "internal": m["internal"],
            "external": m["external"],
            "total": total,
            "grade": grade
        }
        res = db.marks.update_one(
            {"student_id": m["student_id"], "course_id": m["course_id"]},
            {"$set": mark_doc},
            upsert=True
        )
        if res.upserted_id:
            inserted_marks += 1
    print(f"  [OK] Marks: {inserted_marks} new added, {len(raw_marks)} total verified.")

    # 5. SAMPLE ATTENDANCE (Including intentional low attendance <75% for testing!)
    raw_attendance = [
        {"student_id": "STU001", "course_id": "CS101", "classes_held": 40, "classes_attended": 37}, # 92.5%
        {"student_id": "STU001", "course_id": "CS102", "classes_held": 40, "classes_attended": 35}, # 87.5%
        {"student_id": "STU001", "course_id": "CS103", "classes_held": 35, "classes_attended": 30}, # 85.71%
        {"student_id": "STU002", "course_id": "CS101", "classes_held": 40, "classes_attended": 38}, # 95.0%
        {"student_id": "STU002", "course_id": "CS102", "classes_held": 40, "classes_attended": 28}, # 70.0% LOW!
        {"student_id": "STU003", "course_id": "EC101", "classes_held": 45, "classes_attended": 42}, # 93.33%
        {"student_id": "STU003", "course_id": "MA101", "classes_held": 45, "classes_attended": 30}, # 66.67% LOW!
        {"student_id": "STU004", "course_id": "EC101", "classes_held": 45, "classes_attended": 44}, # 97.78%
        {"student_id": "STU005", "course_id": "MA101", "classes_held": 40, "classes_attended": 24}, # 60.0% LOW!
        {"student_id": "STU005", "course_id": "CS101", "classes_held": 40, "classes_attended": 27}, # 67.5% LOW!
        {"student_id": "STU006", "course_id": "CS103", "classes_held": 35, "classes_attended": 32}, # 91.43%
        {"student_id": "STU007", "course_id": "MA101", "classes_held": 40, "classes_attended": 36}, # 90.0%
        {"student_id": "STU008", "course_id": "CS102", "classes_held": 40, "classes_attended": 34}  # 85.0%
    ]

    inserted_attendance = 0
    for a in raw_attendance:
        pct = round((a["classes_attended"] / a["classes_held"]) * 100, 2)
        att_doc = {
            "student_id": a["student_id"],
            "course_id": a["course_id"],
            "classes_held": a["classes_held"],
            "classes_attended": a["classes_attended"],
            "attendance_percentage": pct
        }
        res = db.attendance.update_one(
            {"student_id": a["student_id"], "course_id": a["course_id"]},
            {"$set": att_doc},
            upsert=True
        )
        if res.upserted_id:
            inserted_attendance += 1
    print(f"  [OK] Attendance: {inserted_attendance} new added, {len(raw_attendance)} total verified.")

    print("\n[SUCCESS] Sample data successfully populated into MongoDB database 'student_management'!")
    return True

if __name__ == '__main__':
    seed_sample_data()
