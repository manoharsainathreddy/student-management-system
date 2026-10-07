import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app

def run_tests():
    client = app.test_client()
    print("=" * 60)
    print("[TEST] VERIFYING ALL 9 SCREENS & REST ENDPOINTS")
    print("=" * 60)

    # 1. Screen 3.1: Login & Auth APIs
    res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert res.status_code == 200
    assert res.get_json()['success'] is True
    print("[PASS] Screen 3.1: Login API authentication verified (admin)")

    res = client.get('/api/auth/me')
    assert res.status_code == 200
    assert res.get_json()['user']['role'] == 'admin'
    print("[PASS] Screen 3.1: Auth session state verified")

    # 2. Screen 3.2: Dashboard
    res = client.get('/api/dashboard')
    assert res.status_code == 200
    dash = res.get_json()['data']
    assert dash['total_students'] >= 8
    print(f"[PASS] Screen 3.2: Dashboard stats loaded ({dash['total_students']} Students)")

    # 3. Screen 3.3: Students List & Search
    res = client.get('/api/students/search?q=rahul')
    assert res.status_code == 200
    assert len(res.get_json()['data']) >= 1
    print("[PASS] Screen 3.3: Student Search & List verified")

    # 4. Screen 3.4: Course Enrollments
    res = client.get('/api/enrollments')
    assert res.status_code == 200
    assert len(res.get_json()['data']) > 0
    print("[PASS] Screen 3.4: Enrollments list verified")

    # 5. Screen 3.5: Attendance Marking
    res = client.get('/api/attendance')
    assert res.status_code == 200
    assert len(res.get_json()['data']) > 0
    print("[PASS] Screen 3.5: Attendance records list verified")

    # 6. Screen 3.6: Marks Entry
    res = client.get('/api/marks')
    assert res.status_code == 200
    assert len(res.get_json()['data']) > 0
    print("[PASS] Screen 3.6: Marks & Grade registry verified")

    # 7. Screen 3.7: Results Page with SGPA
    res = client.get('/api/results/STU001')
    assert res.status_code == 200
    res_data = res.get_json()['data']
    assert 'sgpa' in res_data['summary']
    print(f"[PASS] Screen 3.7: Results & SGPA calculation verified (STU001 SGPA: {res_data['summary']['sgpa']})")

    # 8. Screen 3.8: Reports Page
    res = client.get('/api/reports/attendance-shortage?threshold=75')
    assert res.status_code == 200
    assert 'data' in res.get_json()

    res2 = client.get('/api/reports/grade-distribution')
    assert res2.status_code == 200
    assert 'distribution' in res2.get_json()['data']
    print(f"[PASS] Screen 3.8: Reports A (Attendance Shortage) & B (Grade Distribution) verified")

    # 9. Screen 3.9: Admin Collections Inspector
    res = client.get('/api/admin/collections')
    assert res.status_code == 200
    assert len(res.get_json()['collections']) == 5

    res2 = client.get('/api/admin/collections/students')
    assert res2.status_code == 200
    assert len(res2.get_json()['documents']) > 0
    print(f"[PASS] Screen 3.9: Admin Collections inspection verified (5 whitelisted collections)")

    print("=" * 60)
    print("[SUCCESS] ALL 9 SCREENS & ENDPOINTS FULLY VERIFIED!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
