import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { coursesApi } from '../services/api';
import './Dashboard.css';

function Dashboard() {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadCourses();
    }, []);

    // Mock courses for MVP fallback
    const mockCourses = [
        { id: 1, name: 'Data Structures & Algorithms', code: 'CS201', description: 'Learn fundamental data structures including arrays, linked lists, trees, graphs, and essential algorithms for searching and sorting.', progress: 45 },
        { id: 2, name: 'Signal Processing', code: 'EE301', description: 'Study analog and digital signal processing, Fourier transforms, filtering, and real-world applications.', progress: 30 },
        { id: 3, name: 'Thermodynamics', code: 'ME201', description: 'Explore laws of thermodynamics, heat engines, entropy, and energy transfer mechanisms.', progress: 60 },
        { id: 4, name: 'Digital Signal Processing', code: 'EE401', description: 'Advanced DSP concepts including FFT, digital filters, and modern signal processing techniques.', progress: 25 }
    ];

    const loadCourses = async () => {
        try {
            const data = await coursesApi.getAll();
            setCourses(data.courses || []);
        } catch (err) {
            // Fallback to mock data for MVP
            console.log('Using mock course data for MVP demo');
            setCourses(mockCourses);
        } finally {
            setLoading(false);
        }
    };

    const getMasteryColor = (progress) => {
        if (progress >= 80) return 'complete';
        if (progress >= 60) return 'high';
        if (progress >= 30) return 'medium';
        return 'low';
    };

    const getCourseIcon = (name) => {
        const n = name.toLowerCase();
        if (n.includes('data') || n.includes('algorithm')) return '🔢';
        if (n.includes('signal')) return '📡';
        if (n.includes('thermo')) return '🔥';
        if (n.includes('dsp') || n.includes('digital')) return '📊';
        return '📚';
    };

    if (loading) {
        return (
            <div className="container">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading courses...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container">
                <div className="error-state card">
                    <span className="error-icon">⚠️</span>
                    <h3>Connection Error</h3>
                    <p>{error}</p>
                    <button onClick={loadCourses} className="btn btn-primary">
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="container dashboard">
            {/* Header */}
            <div className="dashboard-header animate-slideUp">
                <div className="header-content">
                    <h1>Welcome Back! 👋</h1>
                    <p>Choose a course to continue your learning journey</p>
                </div>
                <div className="header-stats">
                    <div className="stat-item">
                        <span className="stat-value">{courses.length}</span>
                        <span className="stat-label">Courses</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-value">
                            {Math.round(courses.reduce((acc, c) => acc + (c.progress || 0), 0) / courses.length) || 0}%
                        </span>
                        <span className="stat-label">Avg Progress</span>
                    </div>
                </div>
            </div>

            {/* Course Grid */}
            <div className="courses-grid">
                {courses.map((course, index) => (
                    <Link
                        to={`/course/${course.id}`}
                        key={course.id}
                        className="course-card card animate-slideUp"
                        style={{ animationDelay: `${index * 100}ms` }}
                    >
                        <div className="course-header">
                            <span className="course-icon">{getCourseIcon(course.name)}</span>
                            <span className={`course-badge badge badge-${getMasteryColor(course.progress)}`}>
                                {course.progress || 0}% Complete
                            </span>
                        </div>

                        <h3 className="course-name">{course.name}</h3>
                        <p className="course-code">{course.code}</p>
                        <p className="course-description">
                            {course.description?.substring(0, 100)}
                            {course.description?.length > 100 ? '...' : ''}
                        </p>

                        <div className="course-progress">
                            <div className="progress-bar">
                                <div
                                    className={`progress-fill progress-${getMasteryColor(course.progress)}`}
                                    style={{ width: `${course.progress || 0}%` }}
                                ></div>
                            </div>
                        </div>

                        <div className="course-actions">
                            <span className="action-hint">Click to view course →</span>
                        </div>
                    </Link>
                ))}
            </div>

            {courses.length === 0 && (
                <div className="empty-state card">
                    <span className="empty-icon">📚</span>
                    <h3>No Courses Yet</h3>
                    <p>Courses will appear here once the backend initializes them.</p>
                </div>
            )}

            {/* Quick Actions */}
            <div className="quick-actions animate-slideUp" style={{ animationDelay: '400ms' }}>
                <h2>Quick Actions</h2>
                <div className="actions-grid">
                    <Link to="/progress" className="action-card card interactive">
                        <span className="action-icon">📊</span>
                        <div className="action-content">
                            <h4>View Progress</h4>
                            <p>Track your mastery across all topics</p>
                        </div>
                    </Link>
                    <Link to="/ask" className="action-card card interactive">
                        <span className="action-icon">💬</span>
                        <div className="action-content">
                            <h4>Ask AI</h4>
                            <p>Get answers from course materials</p>
                        </div>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
