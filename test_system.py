import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app

def run_tests():
    client = app.test_client()
    print("=" * 60)
    print("[TEST] RUNNING END-TO-END AUTOMATED TEST SUITE FOR STUDENT MANAGEMENT SYSTEM")
    print("=" * 60)

    # 1. Health Check
    res = client.get('/api/health')
    assert res.status_code == 200
    print("[PASS] 1. Health Check & MongoDB Connection verified")

    # 2. Get Students & Search
    res = client.get('/api/students')
    assert res.status_code == 200
    assert res.get_json()['count'] >= 8
    print(f"[PASS] 2. Read Students List (Total: {res.get_json()['count']})")

    res = client.get('/api/students/search?q=rahul')
    assert res.status_code == 200
    assert len(res.get_json()['data']) >= 1
    print("[PASS] 3. Student Search (query='rahul') returned matching record")

    # 3. Test Student Full Profile View
    res = client.get('/api/students/STU001/full')
    assert res.status_code == 200
    profile = res.get_json()['data']
    assert profile['student']['student_id'] == 'STU001'
    assert len(profile['enrollments']) > 0
    assert len(profile['marks']) > 0
    assert len(profile['attendance']) > 0
    print("[PASS] 4. Student Full Profile Aggregation View verified for STU001")

    # 4. Duplicate Student ID validation (Should fail with 400)
    res = client.post('/api/students', json={
        "student_id": "STU001",
        "name": "Duplicate Student",
        "email": "dup@gmail.com",
        "phone": "1234567890",
        "department": "Computer Science",
        "year": 1,
        "semester": 1
    })
    assert res.status_code == 400
    assert "already exists" in res.get_json()['message']
    print("[PASS] 5. Validation test: Duplicate Student ID correctly rejected")

    # 5. Invalid Marks validation (Internal > 30 should fail)
    res = client.post('/api/marks', json={
        "student_id": "STU001",
        "course_id": "CS101",
        "internal": 40,
        "external": 50
    })
    assert res.status_code == 400
    assert "between 0 and 30" in res.get_json()['message']
    print("[PASS] 6. Validation test: Invalid Internal Marks (>30) correctly rejected")

    # 6. Valid Marks submission & backend calculation check
    res = client.post('/api/marks', json={
        "student_id": "STU001",
        "course_id": "CS101",
        "internal": 20,
        "external": 70
    })
    assert res.status_code == 200
    m_data = res.get_json()['data']
    assert m_data['total'] == 90.0
    assert m_data['grade'] == 'A+'
    print(f"[PASS] 7. Marks calculation test: Internal=20, External=70 -> Total={m_data['total']}, Grade={m_data['grade']}")

    # 7. Invalid Attendance validation (Attended > Held should fail)
    res = client.post('/api/attendance', json={
        "student_id": "STU001",
        "course_id": "CS101",
        "classes_held": 20,
        "classes_attended": 25
    })
    assert res.status_code == 400
    assert "cannot exceed" in res.get_json()['message']
    print("[PASS] 8. Validation test: Classes Attended > Held correctly rejected")

    # 8. Valid Attendance submission & percentage calculation
    res = client.post('/api/attendance', json={
        "student_id": "STU001",
        "course_id": "CS101",
        "classes_held": 40,
        "classes_attended": 36
    })
    assert res.status_code == 200
    att_data = res.get_json()['data']
    assert att_data['attendance_percentage'] == 90.0
    print(f"[PASS] 9. Attendance calculation test: Held=40, Attended=36 -> {att_data['attendance_percentage']}%")

    # 9. Duplicate Enrollment validation
    res = client.post('/api/enrollments', json={
        "student_id": "STU001",
        "course_id": "CS101",
        "semester": 4
    })
    assert res.status_code == 400
    assert "already enrolled" in res.get_json()['message']
    print("[PASS] 10. Validation test: Duplicate Enrollment correctly rejected")

    # 10. Dashboard Aggregations
    res = client.get('/api/dashboard')
    assert res.status_code == 200
    dash = res.get_json()['data']
    assert dash['total_students'] >= 8
    assert dash['total_courses'] >= 5
    assert len(dash['students_by_department']) > 0
    assert len(dash['grade_distribution']) > 0
    assert len(dash['low_attendance_students']) > 0
    print(f"[PASS] 11. Dashboard Aggregations verified: {dash['total_students']} Students, {dash['total_courses']} Courses, {len(dash['low_attendance_students'])} Low Attendance (<75%) records")

    # 11. Student Creation & Cascade Delete
    test_stu_id = "STU999"
    res = client.post('/api/students', json={
        "student_id": test_stu_id,
        "name": "Test Temp Student",
        "email": "tempstu999@gmail.com",
        "phone": "9999999999",
        "department": "Computer Science",
        "year": 1,
        "semester": 1
    })
    assert res.status_code == 201

    # Enroll temp student
    client.post('/api/enrollments', json={"student_id": test_stu_id, "course_id": "CS101", "semester": 1})
    client.post('/api/marks', json={"student_id": test_stu_id, "course_id": "CS101", "internal": 15, "external": 35})
    client.post('/api/attendance', json={"student_id": test_stu_id, "course_id": "CS101", "classes_held": 20, "classes_attended": 18})

    # Delete temp student & verify cascade
    res = client.delete(f'/api/students/{test_stu_id}')
    assert res.status_code == 200
    cascaded = res.get_json()['cascaded']
    assert cascaded['enrollments'] == 1
    assert cascaded['marks'] == 1
    assert cascaded['attendance'] == 1
    print(f"[PASS] 12. Student Creation & Cascade Delete verified (Cascaded enrollments: {cascaded['enrollments']}, marks: {cascaded['marks']}, attendance: {cascaded['attendance']})")

    print("=" * 60)
    print("[SUCCESS] ALL 12 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
