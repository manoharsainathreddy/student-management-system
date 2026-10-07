/**
 * Student Management System - Client Side Engine
 * Vanilla JavaScript + Fetch API
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Toast Notification Helper
    window.showToast = function(message, type = 'success') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const icon = type === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    };

    // 2. Generic Fetch API Wrapper
    window.apiFetch = async function(url, options = {}) {
        try {
            const defaultHeaders = { 'Content-Type': 'application/json' };
            options.headers = { ...defaultHeaders, ...(options.headers || {}) };

            const response = await fetch(url, options);
            const data = await response.json();

            if (!response.ok || data.success === false) {
                throw new Error(data.message || `Request failed with status ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API Error (${url}):`, error);
            showToast(error.message, 'error');
            throw error;
        }
    };

    // 3. Modal Helpers
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('active');
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('active');
    };

    // Global Modal Overlay Click to Close
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Page Specific Initializers based on current path
    const path = window.location.pathname;

    if (path === '/' || path.includes('index')) {
        initDashboard();
    } else if (path.includes('students')) {
        initStudentsPage();
    } else if (path.includes('courses')) {
        initCoursesPage();
    } else if (path.includes('enrollments')) {
        initEnrollmentsPage();
    } else if (path.includes('marks')) {
        initMarksPage();
    } else if (path.includes('attendance')) {
        initAttendancePage();
    }
});

/* ==========================================================================
   1. DASHBOARD PAGE
   ========================================================================== */
async function initDashboard() {
    try {
        const res = await apiFetch('/api/dashboard');
        const data = res.data;

        // Cards
        document.getElementById('stat-total-students').textContent = data.total_students || 0;
        document.getElementById('stat-total-courses').textContent = data.total_courses || 0;
        document.getElementById('stat-total-enrollments').textContent = data.total_enrollments || 0;
        document.getElementById('stat-avg-marks').textContent = `${data.average_marks || 0}%`;
        document.getElementById('stat-avg-attendance').textContent = `${data.average_attendance || 0}%`;

        // Department Breakdown Progress Bars
        const deptContainer = document.getElementById('dept-breakdown-container');
        if (deptContainer) {
            deptContainer.innerHTML = '';
            if (!data.students_by_department || data.students_by_department.length === 0) {
                deptContainer.innerHTML = '<p class="text-muted">No department data available.</p>';
            } else {
                const maxCount = Math.max(...data.students_by_department.map(d => d.count), 1);
                const fills = ['fill-indigo', 'fill-emerald', 'fill-amber', 'fill-rose'];

                data.students_by_department.forEach((dept, idx) => {
                    const percentage = Math.round((dept.count / maxCount) * 100);
                    const fillClass = fills[idx % fills.length];

                    const item = document.createElement('div');
                    item.className = 'dept-item';
                    item.innerHTML = `
                        <div class="item-meta">
                            <label>${dept.department}</label>
                            <span>${dept.count} Students</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill ${fillClass}" style="width: ${percentage}%"></div>
                        </div>
                    `;
                    deptContainer.appendChild(item);
                });
            }
        }

        // Grade Distribution
        const gradeContainer = document.getElementById('grade-distribution-container');
        if (gradeContainer) {
            gradeContainer.innerHTML = '';
            if (!data.grade_distribution || data.grade_distribution.length === 0) {
                gradeContainer.innerHTML = '<p class="text-muted">No grade data available.</p>';
            } else {
                const totalMarksCount = data.grade_distribution.reduce((acc, g) => acc + g.count, 0) || 1;
                data.grade_distribution.forEach(g => {
                    const gradeClass = getGradeBadgeClass(g.grade);
                    const percentage = Math.round((g.count / totalMarksCount) * 100);

                    const item = document.createElement('div');
                    item.className = 'grade-item';
                    item.innerHTML = `
                        <div class="item-meta">
                            <label><span class="badge ${gradeClass}">${g.grade}</span></label>
                            <span>${g.count} (${percentage}%)</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill fill-indigo" style="width: ${percentage}%"></div>
                        </div>
                    `;
                    gradeContainer.appendChild(item);
                });
            }
        }

        // Low Attendance Table
        const lowAttBody = document.getElementById('low-attendance-tbody');
        if (lowAttBody) {
            lowAttBody.innerHTML = '';
            if (!data.low_attendance_students || data.low_attendance_students.length === 0) {
                lowAttBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--accent-emerald);">🎉 All students have satisfactory attendance (>= 75%)!</td></tr>';
            } else {
                data.low_attendance_students.forEach(st => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${st.student_id}</strong></td>
                        <td>${st.student_name || 'N/A'}</td>
                        <td>${st.course_id} - ${st.course_name || ''}</td>
                        <td>${st.classes_attended} / ${st.classes_held}</td>
                        <td><span class="badge badge-att-low">${st.attendance_percentage}% (Low)</span></td>
                    `;
                    lowAttBody.appendChild(tr);
                });
            }
        }

    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

/* Helper for grade badge styling */
function getGradeBadgeClass(grade) {
    switch(grade) {
        case 'A+': return 'badge-grade-aplus';
        case 'A': return 'badge-grade-a';
        case 'B+': return 'badge-grade-bplus';
        case 'B': return 'badge-grade-b';
        case 'C': return 'badge-grade-c';
        case 'D': return 'badge-grade-d';
        case 'F': return 'badge-grade-f';
        default: return 'badge-dept';
    }
}

/* ==========================================================================
   2. STUDENTS PAGE
   ========================================================================== */
let allStudentsList = [];

async function initStudentsPage() {
    loadStudentsTable();

    // Live search debouncer
    const searchInput = document.getElementById('student-search-input');
    if (searchInput) {
        let timer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                const query = e.target.value.trim();
                loadStudentsTable(query);
            }, 300);
        });
    }

    // Add Student Form Handler
    const addForm = document.getElementById('student-form');
    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const isEdit = document.getElementById('student-is-edit').value === 'true';
            const studentId = document.getElementById('student_id').value.trim();

            const payload = {
                student_id: studentId,
                name: document.getElementById('name').value.trim(),
                email: document.getElementById('email').value.trim(),
                phone: document.getElementById('phone').value.trim(),
                department: document.getElementById('department').value.trim(),
                year: parseInt(document.getElementById('year').value),
                semester: parseInt(document.getElementById('semester').value)
            };

            try {
                let res;
                if (isEdit) {
                    res = await apiFetch(`/api/students/${studentId}`, {
                        method: 'PUT',
                        body: JSON.stringify(payload)
                    });
                } else {
                    res = await apiFetch('/api/students', {
                        method: 'POST',
                        body: JSON.stringify(payload)
                    });
                }

                showToast(res.message, 'success');
                closeModal('student-modal');
                addForm.reset();
                loadStudentsTable();
            } catch (err) {
                // handled by apiFetch toast
            }
        });
    }
}

async function loadStudentsTable(searchQuery = '') {
    const tbody = document.getElementById('students-tbody');
    if (!tbody) return;

    try {
        const url = searchQuery ? `/api/students/search?q=${encodeURIComponent(searchQuery)}` : '/api/students';
        const res = await apiFetch(url);
        allStudentsList = res.data || [];

        tbody.innerHTML = '';
        if (allStudentsList.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;" class="text-muted">No student records found.</td></tr>';
            return;
        }

        allStudentsList.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong class="text-cyan">${s.student_id}</strong></td>
                <td><strong>${s.name}</strong></td>
                <td>${s.email}</td>
                <td>${s.phone}</td>
                <td><span class="badge badge-dept">${s.department}</span></td>
                <td>Year ${s.year}</td>
                <td>Semester ${s.semester}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="viewStudentProfile('${s.student_id}')" title="View Full Profile">
                        <i class="fa-solid fa-eye"></i> View
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="editStudent('${s.student_id}')" title="Edit Student">
                        <i class="fa-solid fa-pen"></i> Edit
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteStudent('${s.student_id}', '${s.name}')" title="Delete Student">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--accent-rose);">Failed to load students.</td></tr>';
    }
}

window.openAddStudentModal = function() {
    const form = document.getElementById('student-form');
    if (form) form.reset();
    document.getElementById('student-modal-title').textContent = 'Add New Student';
    document.getElementById('student-is-edit').value = 'false';
    document.getElementById('student_id').readOnly = false;
    openModal('student-modal');
};

window.editStudent = function(studentId) {
    const student = allStudentsList.find(s => s.student_id === studentId);
    if (!student) return;

    document.getElementById('student-modal-title').textContent = 'Edit Student Details';
    document.getElementById('student-is-edit').value = 'true';
    document.getElementById('student_id').value = student.student_id;
    document.getElementById('student_id').readOnly = true;

    document.getElementById('name').value = student.name;
    document.getElementById('email').value = student.email;
    document.getElementById('phone').value = student.phone;
    document.getElementById('department').value = student.department;
    document.getElementById('year').value = student.year;
    document.getElementById('semester').value = student.semester;

    openModal('student-modal');
};

window.deleteStudent = async function(studentId, name) {
    if (!confirm(`⚠️ WARNING: Are you sure you want to delete student '${name}' (${studentId})?\n\nThis will also cascade delete all associated enrollments, marks, and attendance records!`)) {
        return;
    }

    try {
        const res = await apiFetch(`/api/students/${studentId}`, { method: 'DELETE' });
        showToast(res.message, 'success');
        loadStudentsTable();
    } catch (err) {
        // Handled in apiFetch
    }
};

window.viewStudentProfile = async function(studentId) {
    try {
        const res = await apiFetch(`/api/students/${studentId}/full`);
        const data = res.data;
        const st = data.student;

        // Modal Header Meta
        document.getElementById('profile-name').textContent = st.name;
        document.getElementById('profile-id-dept').textContent = `${st.student_id} | ${st.department} (Year ${st.year}, Sem ${st.semester})`;
        document.getElementById('profile-contact').textContent = `📧 ${st.email} | 📞 ${st.phone}`;

        // Courses list
        const coursesTbody = document.getElementById('profile-courses-tbody');
        coursesTbody.innerHTML = '';
        if (data.enrollments.length === 0) {
            coursesTbody.innerHTML = '<tr><td colspan="3" class="text-muted">Not enrolled in any courses.</td></tr>';
        } else {
            data.enrollments.forEach(c => {
                coursesTbody.innerHTML += `
                    <tr>
                        <td><strong>${c.course_id}</strong></td>
                        <td>${c.course_name}</td>
                        <td>${c.credits} Credits</td>
                    </tr>
                `;
            });
        }

        // Marks list
        const marksTbody = document.getElementById('profile-marks-tbody');
        marksTbody.innerHTML = '';
        if (data.marks.length === 0) {
            marksTbody.innerHTML = '<tr><td colspan="5" class="text-muted">No marks recorded yet.</td></tr>';
        } else {
            data.marks.forEach(m => {
                const gradeClass = getGradeBadgeClass(m.grade);
                marksTbody.innerHTML += `
                    <tr>
                        <td><strong>${m.course_name}</strong></td>
                        <td>${m.internal} / 30</td>
                        <td>${m.external} / 70</td>
                        <td><strong>${m.total} / 100</strong></td>
                        <td><span class="badge ${gradeClass}">${m.grade}</span></td>
                    </tr>
                `;
            });
        }

        // Attendance list
        const attTbody = document.getElementById('profile-att-tbody');
        attTbody.innerHTML = '';
        if (data.attendance.length === 0) {
            attTbody.innerHTML = '<tr><td colspan="4" class="text-muted">No attendance records found.</td></tr>';
        } else {
            data.attendance.forEach(a => {
                const isLow = a.attendance_percentage < 75;
                const badgeClass = isLow ? 'badge-att-low' : 'badge-att-good';
                const statusText = isLow ? ' (Low)' : '';

                attTbody.innerHTML += `
                    <tr>
                        <td><strong>${a.course_name}</strong></td>
                        <td>${a.classes_held}</td>
                        <td>${a.classes_attended}</td>
                        <td><span class="badge ${badgeClass}">${a.attendance_percentage}%${statusText}</span></td>
                    </tr>
                `;
            });
        }

        openModal('student-profile-modal');
    } catch (err) {
        // error handling
    }
};

/* ==========================================================================
   3. COURSES PAGE
   ========================================================================== */
let allCoursesList = [];

async function initCoursesPage() {
    loadCoursesTable();

    const addForm = document.getElementById('course-form');
    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const isEdit = document.getElementById('course-is-edit').value === 'true';
            const courseId = document.getElementById('course_id').value.trim().toUpperCase();

            const payload = {
                course_id: courseId,
                course_name: document.getElementById('course_name').value.trim(),
                credits: parseInt(document.getElementById('credits').value),
                department: document.getElementById('department').value.trim()
            };

            try {
                let res;
                if (isEdit) {
                    res = await apiFetch(`/api/courses/${courseId}`, {
                        method: 'PUT',
                        body: JSON.stringify(payload)
                    });
                } else {
                    res = await apiFetch('/api/courses', {
                        method: 'POST',
                        body: JSON.stringify(payload)
                    });
                }

                showToast(res.message, 'success');
                closeModal('course-modal');
                addForm.reset();
                loadCoursesTable();
            } catch (err) {
                // Handled
            }
        });
    }
}

async function loadCoursesTable() {
    const tbody = document.getElementById('courses-tbody');
    if (!tbody) return;

    try {
        const res = await apiFetch('/api/courses');
        allCoursesList = res.data || [];

        tbody.innerHTML = '';
        if (allCoursesList.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-muted" style="text-align:center;">No courses found.</td></tr>';
            return;
        }

        allCoursesList.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong class="text-cyan">${c.course_id}</strong></td>
                <td><strong>${c.course_name}</strong></td>
                <td>${c.credits} Credits</td>
                <td><span class="badge badge-dept">${c.department}</span></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="editCourse('${c.course_id}')" title="Edit Course">
                        <i class="fa-solid fa-pen"></i> Edit
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteCourse('${c.course_id}', '${c.course_name}')" title="Delete Course">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--accent-rose);">Failed to load courses.</td></tr>';
    }
}

window.openAddCourseModal = function() {
    const form = document.getElementById('course-form');
    if (form) form.reset();
    document.getElementById('course-modal-title').textContent = 'Add New Course';
    document.getElementById('course-is-edit').value = 'false';
    document.getElementById('course_id').readOnly = false;
    openModal('course-modal');
};

window.editCourse = function(courseId) {
    const course = allCoursesList.find(c => c.course_id === courseId);
    if (!course) return;

    document.getElementById('course-modal-title').textContent = 'Edit Course Details';
    document.getElementById('course-is-edit').value = 'true';
    document.getElementById('course_id').value = course.course_id;
    document.getElementById('course_id').readOnly = true;

    document.getElementById('course_name').value = course.course_name;
    document.getElementById('credits').value = course.credits;
    document.getElementById('department').value = course.department;

    openModal('course-modal');
};

window.deleteCourse = async function(courseId, name) {
    if (!confirm(`⚠️ Are you sure you want to delete course '${name}' (${courseId})?\n\nThis will also remove all associated enrollments, marks, and attendance records!`)) {
        return;
    }

    try {
        const res = await apiFetch(`/api/courses/${courseId}`, { method: 'DELETE' });
        showToast(res.message, 'success');
        loadCoursesTable();
    } catch (err) {
        // Handled
    }
};

/* ==========================================================================
   4. ENROLLMENTS PAGE
   ========================================================================== */
async function initEnrollmentsPage() {
    populateStudentCourseDropdowns('enroll-student-select', 'enroll-course-select');
    loadEnrollmentsTable();

    const form = document.getElementById('enrollment-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                student_id: document.getElementById('enroll-student-select').value,
                course_id: document.getElementById('enroll-course-select').value,
                semester: parseInt(document.getElementById('enroll-semester-select').value)
            };

            try {
                const res = await apiFetch('/api/enrollments', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                showToast(res.message, 'success');
                loadEnrollmentsTable();
            } catch (err) {
                // Handled
            }
        });
    }
}

async function loadEnrollmentsTable() {
    const tbody = document.getElementById('enrollments-tbody');
    if (!tbody) return;

    try {
        const res = await apiFetch('/api/enrollments');
        const enrollments = res.data || [];

        tbody.innerHTML = '';
        if (enrollments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-muted" style="text-align:center;">No enrollment records found.</td></tr>';
            return;
        }

        enrollments.forEach(e => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${e.student_id}</strong> - ${e.student_name}</td>
                <td><strong>${e.course_id}</strong> - ${e.course_name}</td>
                <td>Semester ${e.semester}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteEnrollment('${e.student_id}', '${e.course_id}', ${e.semester})">
                        <i class="fa-solid fa-trash"></i> Unenroll
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--accent-rose);">Failed to load enrollments.</td></tr>';
    }
}

window.deleteEnrollment = async function(studentId, courseId, semester) {
    if (!confirm(`Are you sure you want to remove enrollment for ${studentId} in course ${courseId}?`)) return;

    try {
        const res = await apiFetch(`/api/enrollments?student_id=${studentId}&course_id=${courseId}&semester=${semester}`, {
            method: 'DELETE'
        });
        showToast(res.message, 'success');
        loadEnrollmentsTable();
    } catch (err) {}
};

/* ==========================================================================
   5. MARKS PAGE
   ========================================================================== */
async function initMarksPage() {
    populateStudentCourseDropdowns('marks-student-select', 'marks-course-select');
    loadMarksTable();

    // Live calculation listeners for Total and Grade
    const internalInput = document.getElementById('internal_marks');
    const externalInput = document.getElementById('external_marks');

    const updatePreview = () => {
        const internal = parseFloat(internalInput.value) || 0;
        const external = parseFloat(externalInput.value) || 0;
        const total = Math.round((internal + external) * 100) / 100;
        
        document.getElementById('preview-total').textContent = total;
        document.getElementById('preview-grade').textContent = calculateGradeJS(total);
    };

    if (internalInput && externalInput) {
        internalInput.addEventListener('input', updatePreview);
        externalInput.addEventListener('input', updatePreview);
    }

    const form = document.getElementById('marks-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                student_id: document.getElementById('marks-student-select').value,
                course_id: document.getElementById('marks-course-select').value,
                internal: parseFloat(document.getElementById('internal_marks').value),
                external: parseFloat(document.getElementById('external_marks').value)
            };

            try {
                const res = await apiFetch('/api/marks', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                showToast(res.message, 'success');
                loadMarksTable();
            } catch (err) {}
        });
    }
}

function calculateGradeJS(total) {
    if (total >= 90) return 'A+';
    if (total >= 80) return 'A';
    if (total >= 70) return 'B+';
    if (total >= 60) return 'B';
    if (total >= 50) return 'C';
    if (total >= 40) return 'D';
    return 'F';
}

async function loadMarksTable() {
    const tbody = document.getElementById('marks-tbody');
    if (!tbody) return;

    try {
        const res = await apiFetch('/api/marks');
        const marks = res.data || [];

        tbody.innerHTML = '';
        if (marks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-muted" style="text-align:center;">No marks records found.</td></tr>';
            return;
        }

        marks.forEach(m => {
            const gradeClass = getGradeBadgeClass(m.grade);
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${m.student_id}</strong> - ${m.student_name}</td>
                <td><strong>${m.course_id}</strong> - ${m.course_name}</td>
                <td>${m.internal} / 30</td>
                <td>${m.external} / 70</td>
                <td><strong>${m.total}</strong></td>
                <td><span class="badge ${gradeClass}">${m.grade}</span></td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteMarks('${m.student_id}', '${m.course_id}')">
                        <i class="fa-solid fa-trash"></i> Delete
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color: var(--accent-rose);">Failed to load marks.</td></tr>';
    }
}

window.deleteMarks = async function(studentId, courseId) {
    if (!confirm(`Delete marks record for ${studentId} in course ${courseId}?`)) return;
    try {
        const res = await apiFetch(`/api/marks/${studentId}/${courseId}`, { method: 'DELETE' });
        showToast(res.message, 'success');
        loadMarksTable();
    } catch (err) {}
};

/* ==========================================================================
   6. ATTENDANCE PAGE
   ========================================================================== */
async function initAttendancePage() {
    populateStudentCourseDropdowns('att-student-select', 'att-course-select');
    loadAttendanceTable();

    const heldInput = document.getElementById('classes_held');
    const attendedInput = document.getElementById('classes_attended');

    const updateAttPreview = () => {
        const held = parseInt(heldInput.value) || 0;
        const attended = parseInt(attendedInput.value) || 0;
        if (held > 0 && attended >= 0 && attended <= held) {
            const pct = Math.round((attended / held) * 10000) / 100;
            document.getElementById('preview-percentage').textContent = `${pct}%`;
        } else {
            document.getElementById('preview-percentage').textContent = '0%';
        }
    };

    if (heldInput && attendedInput) {
        heldInput.addEventListener('input', updateAttPreview);
        attendedInput.addEventListener('input', updateAttPreview);
    }

    const form = document.getElementById('attendance-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                student_id: document.getElementById('att-student-select').value,
                course_id: document.getElementById('att-course-select').value,
                classes_held: parseInt(document.getElementById('classes_held').value),
                classes_attended: parseInt(document.getElementById('classes_attended').value)
            };

            try {
                const res = await apiFetch('/api/attendance', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                showToast(res.message, 'success');
                loadAttendanceTable();
            } catch (err) {}
        });
    }
}

async function loadAttendanceTable() {
    const tbody = document.getElementById('attendance-tbody');
    if (!tbody) return;

    try {
        const res = await apiFetch('/api/attendance');
        const attendance = res.data || [];

        tbody.innerHTML = '';
        if (attendance.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center;">No attendance records found.</td></tr>';
            return;
        }

        attendance.forEach(a => {
            const isLow = a.attendance_percentage < 75.0;
            const badgeClass = isLow ? 'badge-att-low' : 'badge-att-good';
            const statusLabel = isLow ? 'Low Attendance' : 'Satisfactory';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${a.student_id}</strong> - ${a.student_name}</td>
                <td><strong>${a.course_id}</strong> - ${a.course_name}</td>
                <td>${a.classes_held}</td>
                <td>${a.classes_attended}</td>
                <td><span class="badge ${badgeClass}">${a.attendance_percentage}% (${statusLabel})</span></td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteAttendance('${a.student_id}', '${a.course_id}')">
                        <i class="fa-solid fa-trash"></i> Delete
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--accent-rose);">Failed to load attendance.</td></tr>';
    }
}

window.deleteAttendance = async function(studentId, courseId) {
    if (!confirm(`Delete attendance record for ${studentId} in course ${courseId}?`)) return;
    try {
        const res = await apiFetch(`/api/attendance/${studentId}/${courseId}`, { method: 'DELETE' });
        showToast(res.message, 'success');
        loadAttendanceTable();
    } catch (err) {}
};

/* Dropdown Populate Helper for Form Selects */
async function populateStudentCourseDropdowns(studentSelectId, courseSelectId) {
    const studentSelect = document.getElementById(studentSelectId);
    const courseSelect = document.getElementById(courseSelectId);

    if (studentSelect) {
        try {
            const sRes = await apiFetch('/api/students');
            studentSelect.innerHTML = '<option value="">-- Select Student --</option>';
            (sRes.data || []).forEach(s => {
                studentSelect.innerHTML += `<option value="${s.student_id}">${s.name} (${s.student_id})</option>`;
            });
        } catch (err) {}
    }

    if (courseSelect) {
        try {
            const cRes = await apiFetch('/api/courses');
            courseSelect.innerHTML = '<option value="">-- Select Course --</option>';
            (cRes.data || []).forEach(c => {
                courseSelect.innerHTML += `<option value="${c.course_id}">${c.course_name} (${c.course_id})</option>`;
            });
        } catch (err) {}
    }
}
