import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { progressApi, coursesApi } from '../services/api';
import './ProgressPage.css';

function ProgressPage() {
    const [progress, setProgress] = useState({});
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [recommendations, setRecommendations] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    // Mock data for MVP fallback
    const mockProgress = {
        'Data Structures & Algorithms': {
            course_id: 1,
            average_mastery: 45,
            topics: [
                { topic_name: 'Binary Search Trees', mastery: 70, attempts: 15, correct: 10 },
                { topic_name: 'Hash Tables', mastery: 55, attempts: 12, correct: 7 },
                { topic_name: 'Sorting Algorithms', mastery: 40, attempts: 10, correct: 4 },
                { topic_name: 'Graph Traversal', mastery: 25, attempts: 8, correct: 2 }
            ]
        },
        'Thermodynamics': {
            course_id: 3,
            average_mastery: 60,
            topics: [
                { topic_name: 'First Law', mastery: 80, attempts: 20, correct: 16 },
                { topic_name: 'Second Law', mastery: 65, attempts: 15, correct: 10 },
                { topic_name: 'Entropy', mastery: 45, attempts: 10, correct: 5 }
            ]
        }
    };

    const mockCourses = [
        { id: 1, name: 'Data Structures & Algorithms' },
        { id: 2, name: 'Signal Processing' },
        { id: 3, name: 'Thermodynamics' },
        { id: 4, name: 'Digital Signal Processing' }
    ];

    const loadData = async () => {
        try {
            const [progressData, coursesData] = await Promise.all([
                progressApi.getAll(),
                coursesApi.getAll()
            ]);
            setProgress(progressData || {});
            setCourses(coursesData.courses || []);
        } catch (err) {
            // Fallback to mock data for MVP
            console.log('Using mock progress data for MVP demo');
            setProgress(mockProgress);
            setCourses(mockCourses);
        } finally {
            setLoading(false);
        }
    };

    const loadRecommendations = async (courseId) => {
        try {
            const data = await progressApi.getRecommendations(courseId);
            setRecommendations(data);
        } catch (err) {
            console.error('Error:', err);
        }
    };

    const handleCourseSelect = (courseId) => {
        setSelectedCourse(courseId);
        if (courseId) {
            loadRecommendations(courseId);
        } else {
            setRecommendations(null);
        }
    };

    const getMasteryClass = (mastery) => {
        if (mastery >= 80) return 'complete';
        if (mastery >= 60) return 'high';
        if (mastery >= 30) return 'medium';
        return 'low';
    };

    if (loading) {
        return (
            <div className="container">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading progress...</p>
                </div>
            </div>
        );
    }

    const courseList = Object.entries(progress);

    return (
        <div className="container progress-page">
            <div className="progress-header animate-slideUp">
                <div className="header-content">
                    <h1>📊 Your Progress</h1>
                    <p>Track your mastery across all courses and topics</p>
                </div>

                {courses.length > 0 && (
                    <select
                        className="course-filter form-input"
                        value={selectedCourse || ''}
                        onChange={(e) => handleCourseSelect(e.target.value ? parseInt(e.target.value) : null)}
                    >
                        <option value="">All Courses</option>
                        {courses.map(course => (
                            <option key={course.id} value={course.id}>{course.name}</option>
                        ))}
                    </select>
                )}
            </div>

            {/* Overview Stats */}
            <div className="stats-grid animate-slideUp" style={{ animationDelay: '100ms' }}>
                <div className="stat-card card">
                    <span className="stat-icon">📚</span>
                    <div className="stat-info">
                        <span className="stat-value">{courseList.length}</span>
                        <span className="stat-label">Courses Started</span>
                    </div>
                </div>
                <div className="stat-card card">
                    <span className="stat-icon">🎯</span>
                    <div className="stat-info">
                        <span className="stat-value">
                            {courseList.reduce((acc, [_, data]) => acc + (data.topics?.length || 0), 0)}
                        </span>
                        <span className="stat-label">Topics Tracked</span>
                    </div>
                </div>
                <div className="stat-card card">
                    <span className="stat-icon">⭐</span>
                    <div className="stat-info">
                        <span className="stat-value">
                            {courseList.length > 0
                                ? Math.round(courseList.reduce((acc, [_, data]) =>
                                    acc + (data.average_mastery || 0), 0) / courseList.length)
                                : 0}%
                        </span>
                        <span className="stat-label">Average Mastery</span>
                    </div>
                </div>
            </div>

            {/* Recommendations */}
            {recommendations && recommendations.recommendations?.length > 0 && (
                <div className="recommendations card animate-slideUp" style={{ animationDelay: '150ms' }}>
                    <h3>💡 Recommended Focus Areas</h3>
                    <p className="rec-message">{recommendations.message}</p>
                    <div className="rec-list">
                        {recommendations.recommendations.map((rec, index) => (
                            <div key={index} className="rec-item">
                                <div className="rec-info">
                                    <span className="rec-name">{rec.topic_name}</span>
                                    <span className="rec-details">
                                        {rec.current_mastery}% mastery • ~{rec.questions_needed} questions to improve
                                    </span>
                                </div>
                                <span className={`difficulty-tag ${rec.difficulty}`}>
                                    {rec.difficulty}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Course Progress */}
            <div className="courses-progress animate-slideUp" style={{ animationDelay: '200ms' }}>
                {courseList.length === 0 ? (
                    <div className="empty-state card">
                        <span className="empty-icon">📈</span>
                        <h3>No Progress Yet</h3>
                        <p>Start taking quizzes to track your mastery!</p>
                        <Link to="/" className="btn btn-primary">Browse Courses</Link>
                    </div>
                ) : (
                    courseList
                        .filter(([name]) => !selectedCourse || progress[name]?.course_id === selectedCourse)
                        .map(([courseName, courseData]) => (
                            <div key={courseName} className="course-progress-card card">
                                <div className="course-header">
                                    <div>
                                        <h3>{courseName}</h3>
                                        <p className="topic-count">{courseData.topics?.length || 0} topics</p>
                                    </div>
                                    <div className="overall-mastery">
                                        <span className="mastery-value">{courseData.average_mastery}%</span>
                                        <span className="mastery-label">Overall</span>
                                    </div>
                                </div>

                                <div className="topics-progress">
                                    {courseData.topics?.map((topic, index) => (
                                        <div key={index} className="topic-progress-item">
                                            <div className="topic-info">
                                                <span className="topic-name">{topic.topic_name}</span>
                                                <span className="topic-stats">
                                                    {topic.attempts} attempts • {topic.correct} correct
                                                </span>
                                            </div>
                                            <div className="topic-bar">
                                                <div className="progress-bar">
                                                    <div
                                                        className={`progress-fill progress-${getMasteryClass(topic.mastery)}`}
                                                        style={{ width: `${topic.mastery}%` }}
                                                    ></div>
                                                </div>
                                                <span className="topic-mastery">{topic.mastery}%</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="course-actions">
                                    <Link
                                        to={`/course/${courseData.course_id}/quiz`}
                                        className="btn btn-secondary btn-sm"
                                    >
                                        Take Quiz
                                    </Link>
                                    <Link
                                        to={`/course/${courseData.course_id}`}
                                        className="btn btn-ghost btn-sm"
                                    >
                                        View Course
                                    </Link>
                                </div>
                            </div>
                        ))
                )}
            </div>
        </div>
    );
}

export default ProgressPage;
