import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { coursesApi, roadmapApi } from '../services/api';
import './CoursePage.css';

function CoursePage() {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showPlanModal, setShowPlanModal] = useState(false);
    const [planForm, setPlanForm] = useState({
        goalDate: '',
        hoursPerWeek: 10,
    });
    const [generatingPlan, setGeneratingPlan] = useState(false);

    useEffect(() => {
        loadCourse();
    }, [courseId]);

    const loadCourse = async () => {
        try {
            const data = await coursesApi.getById(courseId);
            setCourse(data);
        } catch (err) {
            console.error('Error loading course:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleGeneratePlan = async (e) => {
        e.preventDefault();
        setGeneratingPlan(true);

        try {
            await roadmapApi.generate(
                parseInt(courseId),
                planForm.goalDate,
                planForm.hoursPerWeek
            );
            navigate(`/course/${courseId}/study`);
        } catch (err) {
            console.error('Error generating plan:', err);
            alert('Failed to generate study plan');
        } finally {
            setGeneratingPlan(false);
        }
    };

    const getMasteryLevel = (mastery) => {
        if (mastery >= 0.8) return { label: 'Mastered', class: 'mastered' };
        if (mastery >= 0.6) return { label: 'Proficient', class: 'proficient' };
        if (mastery >= 0.3) return { label: 'Learning', class: 'learning' };
        return { label: 'Not Started', class: 'not-started' };
    };

    if (loading) {
        return (
            <div className="container">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading course...</p>
                </div>
            </div>
        );
    }

    if (!course) {
        return (
            <div className="container">
                <div className="error-state card">
                    <h3>Course Not Found</h3>
                    <Link to="/" className="btn btn-primary">Back to Dashboard</Link>
                </div>
            </div>
        );
    }

    const topics = course.topics || [];
    const avgMastery = topics.length > 0
        ? Math.round((topics.reduce((acc, t) => acc + (t.mastery || 0), 0) / topics.length) * 100)
        : 0;

    return (
        <div className="container course-page">
            {/* Breadcrumb */}
            <div className="breadcrumb animate-fadeIn">
                <Link to="/">Courses</Link>
                <span className="separator">/</span>
                <span>{course.name}</span>
            </div>

            {/* Course Header */}
            <div className="course-header-section animate-slideUp">
                <div className="course-info">
                    <h1>{course.name}</h1>
                    <p className="course-code-large">{course.code}</p>
                    <p className="course-desc">{course.description}</p>
                </div>

                <div className="course-stats">
                    <div className="stat-circle">
                        <svg viewBox="0 0 100 100">
                            <circle className="bg" cx="50" cy="50" r="45" />
                            <circle
                                className="progress"
                                cx="50" cy="50" r="45"
                                strokeDasharray={`${avgMastery * 2.83} 283`}
                            />
                        </svg>
                        <div className="stat-text">
                            <span className="stat-value">{avgMastery}%</span>
                            <span className="stat-label">Mastery</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="course-actions-bar animate-slideUp" style={{ animationDelay: '100ms' }}>
                <button
                    onClick={() => setShowPlanModal(true)}
                    className="btn btn-primary btn-lg"
                >
                    📅 Create Study Plan
                </button>
                <Link
                    to={`/course/${courseId}/study`}
                    className="btn btn-secondary btn-lg"
                >
                    📖 View Study Board
                </Link>
                <Link
                    to={`/course/${courseId}/quiz`}
                    className="btn btn-secondary btn-lg"
                >
                    🧠 Take Quiz
                </Link>
            </div>

            {/* Topics Grid */}
            <div className="topics-section animate-slideUp" style={{ animationDelay: '200ms' }}>
                <h2>Course Topics</h2>
                <div className="topics-grid">
                    {topics.map((topic, index) => {
                        const level = getMasteryLevel(topic.mastery || 0);
                        return (
                            <div
                                key={topic.id}
                                className={`topic-card card ${level.class}`}
                                style={{ animationDelay: `${index * 50}ms` }}
                            >
                                <div className="topic-header">
                                    <span className="topic-week">Week {topic.week_number || index + 1}</span>
                                    <span className={`topic-level ${level.class}`}>{level.label}</span>
                                </div>
                                <h4 className="topic-name">{topic.name}</h4>
                                <p className="topic-desc">{topic.description}</p>

                                <div className="topic-progress">
                                    <div className="progress-bar">
                                        <div
                                            className="progress-fill"
                                            style={{
                                                width: `${(topic.mastery || 0) * 100}%`,
                                                background: `var(--mastery-${level.class === 'mastered' ? 'complete' : level.class === 'proficient' ? 'high' : level.class === 'learning' ? 'medium' : 'low'})`
                                            }}
                                        ></div>
                                    </div>
                                    <span className="progress-text">{Math.round((topic.mastery || 0) * 100)}%</span>
                                </div>

                                {topic.attempts > 0 && (
                                    <p className="topic-attempts">{topic.attempts} attempts</p>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Study Plan Modal */}
            {showPlanModal && (
                <div className="modal-overlay" onClick={() => setShowPlanModal(false)}>
                    <div className="modal card" onClick={e => e.stopPropagation()}>
                        <h3>Create Study Plan</h3>
                        <p className="modal-subtitle">Set your goal and we'll create a personalized roadmap</p>

                        <form onSubmit={handleGeneratePlan}>
                            <div className="form-group">
                                <label className="form-label">Goal Date (Exam/Deadline)</label>
                                <input
                                    type="date"
                                    className="form-input"
                                    value={planForm.goalDate}
                                    onChange={e => setPlanForm({ ...planForm, goalDate: e.target.value })}
                                    required
                                    min={new Date().toISOString().split('T')[0]}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Study Hours Per Week</label>
                                <input
                                    type="number"
                                    className="form-input"
                                    value={planForm.hoursPerWeek}
                                    onChange={e => setPlanForm({ ...planForm, hoursPerWeek: parseInt(e.target.value) })}
                                    required
                                    min={1}
                                    max={40}
                                />
                            </div>

                            <div className="modal-actions">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => setShowPlanModal(false)}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={generatingPlan}
                                >
                                    {generatingPlan ? 'Generating...' : 'Generate Plan'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default CoursePage;
