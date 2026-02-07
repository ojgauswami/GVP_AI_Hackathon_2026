// Academic Intelligence Engine - State-Driven Interface
// Vanilla JavaScript with no dependencies

class AcademicEngine {
    constructor() {
        this.state = {
            students: [],
            systemPulse: null,
            activeFilter: 'all',
            editMode: false,
            editingStudent: null
        };

        this.elements = {
            addStudentBtn: document.getElementById('add-student-btn'),
            panel: document.getElementById('add-student-panel'),
            panelOverlay: document.getElementById('panel-overlay'),
            panelClose: document.getElementById('panel-close'),
            cancelBtn: document.getElementById('cancel-btn'),
            studentForm: document.getElementById('student-form'),
            studentsList: document.getElementById('students-list'),
            emptyState: document.getElementById('empty-state'),
            formError: document.getElementById('form-error'),
            filterBtns: document.querySelectorAll('.filter-btn')
        };

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadData();
    }

    bindEvents() {
        // Panel controls
        this.elements.addStudentBtn.addEventListener('click', () => this.openPanel());
        this.elements.panelClose.addEventListener('click', () => this.closePanel());
        this.elements.cancelBtn.addEventListener('click', () => this.closePanel());
        this.elements.panelOverlay.addEventListener('click', () => this.closePanel());

        // Form submission
        this.elements.studentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });

        // Filters
        this.elements.filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleFilter(e.target.dataset.filter);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closePanel();
        });
    }

    async loadData() {
        await Promise.all([
            this.fetchSystemPulse(),
            this.fetchStudents()
        ]);
    }

    async fetchSystemPulse() {
        try {
            const response = await fetch('/api/system/pulse');
            const data = await response.json();
            this.state.systemPulse = data;
            this.renderSystemPulse();
        } catch (error) {
            console.error('Failed to fetch system pulse:', error);
        }
    }

    async fetchStudents() {
        try {
            const response = await fetch('/api/students');
            const data = await response.json();
            this.state.students = data;
            this.renderStudents();
        } catch (error) {
            console.error('Failed to fetch students:', error);
        }
    }

    renderSystemPulse() {
        const pulse = this.state.systemPulse;
        if (!pulse) return;

        // Update metrics
        document.getElementById('total-students').textContent = pulse.total_students;
        document.getElementById('attendance-health').textContent = `${pulse.attendance_health.toFixed(0)}%`;
        document.getElementById('at-risk-count').textContent = pulse.students_at_risk;
        document.getElementById('avg-performance').textContent = pulse.average_performance.toFixed(0);

        // Update attendance indicator
        const indicator = document.getElementById('attendance-indicator');
        const healthPercentage = Math.min(100, pulse.attendance_health);
        const healthColor = this.getHealthColor(healthPercentage);

        indicator.style.setProperty('--indicator-width', `${healthPercentage}%`);
        indicator.style.setProperty('--indicator-color', healthColor);

        // Render system insights
        const insightsContainer = document.getElementById('system-insights');
        if (pulse.system_insights && pulse.system_insights.length > 0) {
            insightsContainer.innerHTML = pulse.system_insights
                .map(insight => `<div class="insight-item">${insight}</div>`)
                .join('');
        } else {
            insightsContainer.innerHTML = '';
        }
    }

    renderStudents() {
        const filteredStudents = this.getFilteredStudents();

        if (filteredStudents.length === 0) {
            this.elements.studentsList.innerHTML = '';
            this.elements.emptyState.classList.remove('hidden');
            return;
        }

        this.elements.emptyState.classList.add('hidden');

        this.elements.studentsList.innerHTML = filteredStudents
            .map(student => this.createStudentCard(student))
            .join('');

        // Attach event listeners
        this.attachCardEventListeners();
    }

    attachCardEventListeners() {
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const rollNumber = e.target.dataset.roll;
                const student = this.state.students.find(s => s.roll_number === rollNumber);
                if (student) {
                    this.openPanel(student);
                }
            });
        });

        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const rollNumber = e.target.dataset.roll;
                const student = this.state.students.find(s => s.roll_number === rollNumber);
                if (student && confirm(`Remove ${student.name} from the system?`)) {
                    await this.deleteStudent(rollNumber);
                }
            });
        });
    }

    getFilteredStudents() {
        const filter = this.state.activeFilter;

        if (filter === 'all') {
            return this.state.students;
        }

        return this.state.students.filter(student => student.risk_state === filter);
    }

    createStudentCard(student) {
        const attendance = student.attendance || {};
        const performance = student.performance || {};

        const attendanceColor = this.getAttendanceColor(attendance.attendance_percentage || 0);
        const performanceColor = this.getPerformanceColor(performance.marks || 0);

        const riskBadge = student.risk_state !== 'stable'
            ? `<span class="risk-badge ${student.risk_state}">${student.risk_state === 'critical' ? 'below threshold' : 'requires review'}</span>`
            : '';

        return `
            <div class="student-card" data-risk="${student.risk_state}">
                <div class="student-header">
                    <div class="student-info">
                        <h3>${student.name}</h3>
                        <div class="student-meta">${student.roll_number} · Semester ${student.semester}</div>
                    </div>
                    ${riskBadge}
                </div>
                
                <div class="student-metrics">
                    <div class="metric-item">
                        <div class="metric-item-label">Attendance</div>
                        <div class="metric-item-value">${attendance.attendance_percentage || 0}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="--progress-width: ${attendance.attendance_percentage || 0}%; --progress-color: ${attendanceColor}"></div>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-item-label">Performance</div>
                        <div class="metric-item-value">${performance.marks || 0}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="--progress-width: ${performance.marks || 0}%; --progress-color: ${performanceColor}"></div>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-item-label">Category</div>
                        <div class="metric-item-value" style="font-size: 0.875rem; text-transform: capitalize;">
                            ${performance.category ? performance.category.replace('_', ' ') : 'N/A'}
                        </div>
                    </div>
                </div>
                
                ${student.ai_insight && student.ai_insight !== 'Insufficient data for assessment.'
                ? `<div class="ai-insight">${student.ai_insight}</div>`
                : ''}
                
                <div class="student-actions">
                    <button class="btn-edit" data-roll="${student.roll_number}">Edit</button>
                    <button class="btn-delete" data-roll="${student.roll_number}">Remove</button>
                </div>
            </div>
        `;
    }

    getAttendanceColor(percentage) {
        if (percentage >= 90) return 'var(--color-excellent)';
        if (percentage >= 80) return 'var(--color-stable)';
        if (percentage >= 75) return 'var(--color-warning)';
        return 'var(--color-critical)';
    }

    getPerformanceColor(marks) {
        if (marks >= 75) return 'var(--color-excellent)';
        if (marks >= 50) return 'var(--color-stable)';
        return 'var(--color-critical)';
    }

    getHealthColor(percentage) {
        if (percentage >= 85) return 'var(--color-excellent)';
        if (percentage >= 75) return 'var(--color-stable)';
        if (percentage >= 65) return 'var(--color-warning)';
        return 'var(--color-critical)';
    }

    async handleSubmit() {
        const formData = new FormData(this.elements.studentForm);
        const data = {
            roll_number: formData.get('roll_number'),
            name: formData.get('name'),
            semester: parseInt(formData.get('semester')),
            total_lectures: parseInt(formData.get('total_lectures')),
            attended_lectures: parseInt(formData.get('attended_lectures')),
            marks: parseFloat(formData.get('marks'))
        };

        // Validation
        if (data.attended_lectures > data.total_lectures) {
            this.showFormError('Attended lectures cannot exceed total lectures');
            return;
        }

        try {
            if (this.state.editMode) {
                // Update existing student
                const response = await fetch(`/api/students/${this.state.editingStudent.roll_number}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to update student');
                }
            } else {
                // Add new student
                const response = await fetch('/api/students', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to add student');
                }
            }

            // Success
            this.closePanel();
            this.elements.studentForm.reset();
            await this.loadData();

        } catch (error) {
            this.showFormError(error.message);
        }
    }

    handleFilter(filter) {
        this.state.activeFilter = filter;

        // Update UI
        this.elements.filterBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });

        this.renderStudents();
    }

    openPanel(student = null) {
        if (student) {
            // Edit mode
            this.state.editMode = true;
            this.state.editingStudent = student;
            document.querySelector('.panel-title').textContent = 'Edit Student';
            document.querySelector('.student-form button[type="submit"]').textContent = 'Update Student';

            // Populate form
            document.getElementById('roll-number').value = student.roll_number;
            document.getElementById('roll-number').disabled = true; // Can't change roll number
            document.getElementById('name').value = student.name;
            document.getElementById('semester').value = student.semester;
            document.getElementById('total-lectures').value = student.attendance?.total_lectures || 0;
            document.getElementById('attended-lectures').value = student.attendance?.attended_lectures || 0;
            document.getElementById('marks').value = student.performance?.marks || 0;
        } else {
            // Add mode
            this.state.editMode = false;
            this.state.editingStudent = null;
            document.querySelector('.panel-title').textContent = 'Add Student';
            document.querySelector('.student-form button[type="submit"]').textContent = 'Add Student';
            document.getElementById('roll-number').disabled = false;
        }

        this.elements.panel.classList.add('active');
        this.hideFormError();

        // Focus appropriate input
        setTimeout(() => {
            if (student) {
                document.getElementById('name').focus();
            } else {
                document.getElementById('roll-number').focus();
            }
        }, 300);
    }

    closePanel() {
        this.elements.panel.classList.remove('active');
        this.elements.studentForm.reset();
        this.hideFormError();
        this.state.editMode = false;
        this.state.editingStudent = null;
        document.getElementById('roll-number').disabled = false;
    }

    showFormError(message) {
        this.elements.formError.textContent = message;
        this.elements.formError.classList.add('show');
    }

    hideFormError() {
        this.elements.formError.textContent = '';
        this.elements.formError.classList.remove('show');
    }

    async deleteStudent(rollNumber) {
        try {
            const response = await fetch(`/api/students/${rollNumber}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Failed to remove student');
            }

            await this.loadData();
        } catch (error) {
            alert('Error removing student: ' + error.message);
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.academicEngine = new AcademicEngine();
});
