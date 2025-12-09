/**
 * Teaching Management System - API Client
 * Handles all API communication with the backend
 */

const API_BASE_URL = 'http://localhost:8000';

class TMSApi {
    constructor() {
        this.token = localStorage.getItem('tms_token');
        this.user = JSON.parse(localStorage.getItem('tms_user') || 'null');
    }

    // Helper method for API requests
    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers,
        };

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Network error' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication
    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });

        this.token = data.access_token;
        this.user = data.user;
        localStorage.setItem('tms_token', this.token);
        localStorage.setItem('tms_user', JSON.stringify(this.user));

        return data;
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('tms_token');
        localStorage.removeItem('tms_user');
    }

    // Courses
    async getCourses(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await this.request(`/courses/?${query}`);
    }

    async getCourse(id) {
        return await this.request(`/courses/${id}`);
    }

    async createCourse(data) {
        return await this.request('/courses/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async searchCourses(name) {
        return await this.request(`/courses/search/by-name?name=${encodeURIComponent(name)}`);
    }

    async getCourseCapacity(id) {
        return await this.request(`/courses/${id}/capacity`);
    }

    // Enrollments
    async enrollInCourse(studentId, courseId) {
        return await this.request('/enrollments/', {
            method: 'POST',
            body: JSON.stringify({ student_id: studentId, course_id: courseId }),
        });
    }

    async getStudentEnrollments(studentId) {
        return await this.request(`/enrollments/student/${studentId}`);
    }

    async withdrawFromCourse(enrollmentId) {
        return await this.request(`/enrollments/${enrollmentId}`, {
            method: 'DELETE',
        });
    }

    // Grades
    async getStudentGrades(studentId) {
        return await this.request(`/grades/student/${studentId}`);
    }

    async getCourseGrades(courseId) {
        return await this.request(`/grades/course/${courseId}`);
    }

    async recordGrade(data) {
        return await this.request('/grades/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getCourseStatistics(courseId) {
        return await this.request(`/grades/course/${courseId}/statistics`);
    }

    // Assignments
    async getCourseAssignments(courseId) {
        return await this.request(`/assignments/course/${courseId}`);
    }

    async createAssignment(data) {
        return await this.request('/assignments/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async submitAssignment(assignmentId, studentId, content, file) {
        const formData = new FormData();
        formData.append('student_id', studentId);
        if (content) formData.append('content', content);
        if (file) formData.append('file', file);

        return await fetch(`${API_BASE_URL}/assignments/${assignmentId}/submit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
            },
            body: formData,
        }).then(res => res.json());
    }

    async getAssignmentSubmissions(assignmentId, ungradedOnly = false) {
        const query = ungradedOnly ? '?ungraded_only=true' : '';
        return await this.request(`/assignments/${assignmentId}/submissions${query}`);
    }

    async gradeSubmission(submissionId, score, feedback) {
        return await this.request(`/assignments/submissions/${submissionId}/grade`, {
            method: 'PUT',
            body: JSON.stringify({ score, feedback }),
        });
    }

    // Materials
    async getCourseMaterials(courseId) {
        return await this.request(`/materials/course/${courseId}`);
    }

    async uploadMaterial(courseId, title, description, file) {
        const formData = new FormData();
        formData.append('course_id', courseId);
        formData.append('title', title);
        if (description) formData.append('description', description);
        formData.append('file', file);

        return await fetch(`${API_BASE_URL}/materials/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
            },
            body: formData,
        }).then(res => res.json());
    }

    getMaterialDownloadUrl(materialId) {
        return `${API_BASE_URL}/materials/${materialId}`;
    }

    // Notifications
    async getNotifications(unreadOnly = false) {
        const query = unreadOnly ? '?unread_only=true' : '';
        return await this.request(`/notifications/${query}`);
    }

    async getUnreadCount() {
        return await this.request('/notifications/unread-count');
    }

    async markAsRead(notificationId) {
        return await this.request(`/notifications/${notificationId}/read`, {
            method: 'PUT',
        });
    }

    async markAllAsRead() {
        return await this.request('/notifications/mark-all-read', {
            method: 'PUT',
        });
    }

    // Teachers
    async getTeacherCourses(teacherId) {
        return await this.request(`/teachers/${teacherId}/courses`);
    }

    // Students
    async getStudents() {
        return await this.request('/students/');
    }

    async getStudent(id) {
        return await this.request(`/students/${id}`);
    }

    // Admin
    async getSystemStats() {
        return await this.request('/admin/stats');
    }

    async freezeUser(userId) {
        return await this.request(`/admin/users/${userId}/freeze`, {
            method: 'POST',
        });
    }

    async unfreezeUser(userId) {
        return await this.request(`/admin/users/${userId}/unfreeze`, {
            method: 'POST',
        });
    }
}

// Create global API instance
const api = new TMSApi();

// Utility Functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });
}

function checkAuth() {
    if (!api.token || !api.user) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function requireRole(role) {
    if (!checkAuth()) return false;
    if (api.user.role !== role && api.user.role !== 'admin') {
        showAlert('您没有权限访问此页面', 'error');
        setTimeout(() => window.location.href = 'login.html', 1500);
        return false;
    }
    return true;
}
