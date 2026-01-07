/**
 * Study Pilot AI - API Service
 * Handles all backend communication with authentication
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

// Get stored auth data
const getAuthData = () => {
    const stored = localStorage.getItem('studypilot_auth');
    return stored ? JSON.parse(stored) : null;
};

// Set auth data
const setAuthData = (data) => {
    localStorage.setItem('studypilot_auth', JSON.stringify(data));
};

// Clear auth data
const clearAuthData = () => {
    localStorage.removeItem('studypilot_auth');
};

// Get API key from storage
const getApiKey = () => {
    const auth = getAuthData();
    return auth?.api_key;
};

// Make authenticated request
const fetchWithAuth = async (endpoint, options = {}) => {
    const apiKey = getApiKey();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (apiKey) {
        headers['X-API-Key'] = apiKey;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        clearAuthData();
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }

    return response;
};

// ============ Auth API ============

export const authApi = {
    async login(email, password) {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            setAuthData({ ...data.user, api_key: data.api_key });
        }

        return { ok: response.ok, data };
    },

    async register(name, email, password) {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            setAuthData({ ...data.user, api_key: data.api_key });
        }

        return { ok: response.ok, data };
    },


    logout() {
        clearAuthData();
    },

    getUser() {
        return getAuthData();
    },

    isAuthenticated() {
        return !!getApiKey();
    },
};

// ============ Courses API ============

export const coursesApi = {
    async getAll() {
        const response = await fetchWithAuth('/courses');
        return response.json();
    },

    async getById(courseId) {
        const response = await fetchWithAuth(`/courses/${courseId}`);
        return response.json();
    },
};

// ============ Roadmap API ============

export const roadmapApi = {
    async generate(courseId, goalDate, hoursPerWeek, focusAreas = []) {
        const response = await fetchWithAuth('/roadmap/generate', {
            method: 'POST',
            body: JSON.stringify({
                course_id: courseId,
                goal_date: goalDate,
                hours_per_week: hoursPerWeek,
                focus_areas: focusAreas,
            }),
        });
        return response.json();
    },

    async get(courseId) {
        const response = await fetchWithAuth(`/roadmap/${courseId}`);
        if (response.status === 404) {
            return null;
        }
        return response.json();
    },
};

// ============ Query API ============

export const queryApi = {
    async ask(query, courseId = null, history = []) {
        const response = await fetchWithAuth('/query', {
            method: 'POST',
            body: JSON.stringify({
                query,
                course_id: courseId,
                history: history
            }),
        });
        return response.json();
    },
};

// ============ Quiz API ============

export const quizApi = {
    async generate(courseId, numQuestions = 10, topicId = null) {
        let url = `/quiz/${courseId}?num=${numQuestions}`;
        if (topicId) {
            url += `&topic_id=${topicId}`;
        }
        const response = await fetchWithAuth(url);
        return response.json();
    },

    async submit(quizId, responses) {
        const response = await fetchWithAuth('/quiz/submit', {
            method: 'POST',
            body: JSON.stringify({ quiz_id: quizId, responses }),
        });
        return response.json();
    },
};

// ============ Progress API ============

export const progressApi = {
    async getAll(courseId = null) {
        let url = '/progress';
        if (courseId) {
            url += `?course_id=${courseId}`;
        }
        const response = await fetchWithAuth(url);
        return response.json();
    },

    async getRecommendations(courseId) {
        const response = await fetchWithAuth(`/progress/${courseId}/recommendations`);
        return response.json();
    },
};

// ============ Health API ============

export const healthApi = {
    async check() {
        try {
            const response = await fetch(`${API_BASE}/health`);
            return response.ok;
        } catch {
            return false;
        }
    },
};

export default {
    auth: authApi,
    courses: coursesApi,
    roadmap: roadmapApi,
    query: queryApi,
    quiz: quizApi,
    progress: progressApi,
    health: healthApi,
};
