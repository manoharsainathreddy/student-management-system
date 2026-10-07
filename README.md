# Student Management System (MongoDB + Flask)

A complete, fully functional, full-stack **Student Management System** developed as a college-level **NoSQL & MongoDB demonstration project**.

The application uses **MongoDB Community Server** as its single, dedicated database and is built using Python, Flask, PyMongo, HTML5, Vanilla CSS3, and Vanilla JavaScript.

---

## 🌟 Key Features

1. **Complete Document Modeling**: Uses 5 decoupled collections (`students`, `courses`, `enrollments`, `marks`, `attendance`) connected via `student_id` and `course_id`.
2. **Full CRUD Functionality**: Create, Read, Update, and Delete operations across all entities.
3. **Cascading Deletions**: Automated cleanup of related enrollments, marks, and attendance when deleting students or courses.
4. **Live Search**: Instant, case-insensitive search across student ID, name, email, and department.
5. **Detailed Student Profiles**: Combines student metadata, enrolled courses, marks, grades, and attendance stats in a single integrated view.
6. **Automated Server Calculations**:
   - **Marks**: Total ($internal + external$) and grade ($A+, A, B+, B, C, D, F$) computed strictly on the backend.
   - **Attendance**: Percentage ($\frac{attended}{held} \times 100$) auto-calculated with low attendance detection ($< 75\%$).
7. **MongoDB Aggregation Pipelines**:
   - `$group` by department for student breakdown.
   - `$group` for grade distribution counts.
   - `$group` for overall average total marks & average attendance percentage.
   - `$match` + `$lookup` for retrieving students below 75% attendance.
8. **MongoDB Indexes**: Unique indexes on `student_id`, `email`, and `course_id`, plus compound unique indexes for `enrollments`, `marks`, and `attendance`.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Glassmorphism & Responsive Design), Vanilla JavaScript (Fetch API) |
| **Backend** | Python 3.14, Flask, PyMongo, python-dotenv |
| **Database** | MongoDB Community Server (`mongodb://localhost:27017/`), Database: `student_management` |
| **Database GUI** | MongoDB Compass |

---

## 📁 Project Structure

```text
STUDENT MANAGEMENT SYSTEM/
│
├── app.py                      # Flask application entry point & route definitions
├── config.py                   # Central environment & database configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables configuration
├── README.md                   # Comprehensive project documentation
│
├── database/
│   ├── __init__.py
│   └── mongodb.py              # Central PyMongo connection pooling & index setup
│
├── routes/
│   ├── __init__.py
│   ├── students.py             # Student CRUD & search APIs
│   ├── courses.py              # Course CRUD APIs
│   ├── enrollments.py          # Student-Course enrollment APIs
│   ├── marks.py                # Marks & grade calculation APIs
│   ├── attendance.py           # Attendance & percentage calculation APIs
│   └── dashboard.py            # MongoDB aggregation pipeline endpoints
│
├── templates/
│   ├── index.html              # Dashboard with stats & aggregation views
│   ├── students.html           # Student table, search & full profile view modal
│   ├── courses.html            # Course catalog table & modals
│   ├── enrollments.html        # Enrollment form & list
│   ├── marks.html              # Marks entry form with live calculation & table
│   └── attendance.html         # Attendance entry form with live preview & table
│
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphism dark mode responsive stylesheet
│   └── js/
│       └── script.js           # Fetch API engine, forms & UI interactivity
│
└── sample_data/
    └── sample_data.py          # Data seed script for college demonstration
```

---

## 🗄️ Database Collections & Schema

Database Name: `student_management`

### 1. `students` Collection
```json
{
    "student_id": "STU001",
    "name": "Rahul Kumar",
    "email": "rahul@gmail.com",
    "phone": "9876543210",
    "department": "Computer Science",
    "year": 2,
    "semester": 4
}
```

### 2. `courses` Collection
```json
{
    "course_id": "CS101",
    "course_name": "Database Management Systems",
    "credits": 4,
    "department": "Computer Science"
}
```

### 3. `enrollments` Collection
```json
{
    "student_id": "STU001",
    "course_id": "CS101",
    "semester": 4
}
```

### 4. `marks` Collection
```json
{
    "student_id": "STU001",
    "course_id": "CS101",
    "internal": 28.0,
    "external": 68.0,
    "total": 96.0,
    "grade": "A+"
}
```

### 5. `attendance` Collection
```json
{
    "student_id": "STU001",
    "course_id": "CS101",
    "classes_held": 40,
    "classes_attended": 37,
    "attendance_percentage": 92.5
}
```

---

## 🚀 Installation & Running Guide

### Prerequisites
1. **Python 3.8+** installed.
2. **MongoDB Community Server** installed and running on `localhost:27017`.
3. **MongoDB Compass** (Optional, for database inspection).

### Steps

1. **Open Workspace Directory**:
   ```powershell
   cd "c:\Users\manoh\OneDrive\Desktop\STUDENT MANAGEMENT SYSTEM"
   ```

2. **Activate Virtual Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Seed Database with Sample Data**:
   ```powershell
   python sample_data/sample_data.py
   ```

5. **Start Flask Server**:
   ```powershell
   python app.py
   ```

6. **Open in Browser**:
   Navigate to: `http://127.0.0.1:5000`

---

## 🔍 MongoDB Compass Verification Instructions

1. Launch **MongoDB Compass**.
2. Connect to local MongoDB URI:
   ```text
   mongodb://localhost:27017
   ```
3. Look for the database: `student_management`.
4. Inspect the 5 collections:
   - `students`
   - `courses`
   - `enrollments`
   - `marks`
   - `attendance`
5. Click on the **Indexes** tab of any collection to verify created indexes (`student_id`, `email`, `course_id`, compound unique keys).

---

## ⚡ Indexing & Aggregation Highlights

### Indexing
The system initializes the following indexes on startup (`database/mongodb.py`):
- `students.student_id` (Unique)
- `students.email` (Unique)
- `courses.course_id` (Unique)
- `enrollments` compound `(student_id, course_id, semester)` (Unique)
- `marks` compound `(student_id, course_id)` (Unique)
- `attendance` compound `(student_id, course_id)` (Unique)

### Aggregation Pipelines (`routes/dashboard.py`)
- **Department Breakdown**:
  `db.students.aggregate([{"$group": {"_id": "$department", "count": {"$sum": 1}}}])`
- **Low Attendance Lookup**:
  `db.attendance.aggregate([{"$match": {"attendance_percentage": {"$lt": 75.0}}}, {"$lookup": {"from": "students", ...}}])`

---

## 🧪 Testing Scenarios for Demonstration

1. **Duplicate Student ID**: Attempt adding a student with ID `STU001`. The backend rejects it with `Student ID 'STU001' already exists`.
2. **Invalid Marks**: Enter Internal = 40 (Max is 30). The system rejects with `Internal marks must be between 0 and 30`.
3. **Invalid Attendance**: Enter Held = 30, Attended = 35. The system rejects with `Classes attended cannot exceed total classes held`.
4. **Duplicate Enrollment**: Re-enroll `STU001` in `CS101` for Semester 4. The backend prevents duplicate document creation.
5. **Student Detail Profile**: Click **View** on student `Rahul Kumar` (`STU001`) to view combined enrolled courses, marks, and attendance stats in a single modal.
