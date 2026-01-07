import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { roadmapApi, coursesApi } from '../services/api';
import './StudyBoard.css';

function StudyBoard() {
    const { courseId } = useParams();
    const [roadmap, setRoadmap] = useState(null);
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [expandedWeek, setExpandedWeek] = useState(null);

    useEffect(() => {
        loadData();
    }, [courseId]);

    const loadData = async () => {
        try {
            const [roadmapData, courseData] = await Promise.all([
                roadmapApi.get(courseId),
                coursesApi.getById(courseId)
            ]);
            setRoadmap(roadmapData);
            setCourse(courseData);

            // Auto-expand first incomplete week
            if (roadmapData?.plan?.weeks) {
                const firstIncomplete = roadmapData.plan.weeks.findIndex(w =>
                    new Date(w.end_date) >= new Date()
                );
                setExpandedWeek(firstIncomplete >= 0 ? firstIncomplete : 0);
            }
        } catch (err) {
            console.error('Error loading data:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="container">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading study plan...</p>
                </div>
            </div>
        );
    }

    if (!roadmap) {
        return (
            <div className="container study-board">
                <div className="breadcrumb">
                    <Link to="/">Courses</Link>
                    <span className="separator">/</span>
                    <Link to={`/course/${courseId}`}>{course?.name || 'Course'}</Link>
                    <span className="separator">/</span>
                    <span>Study Plan</span>
                </div>

                <div className="no-plan card">
                    <span className="no-plan-icon">📅</span>
                    <h3>No Study Plan Yet</h3>
                    <p>Create a personalized study plan to get started!</p>
                    <Link to={`/course/${courseId}`} className="btn btn-primary">
                        Create Study Plan
                    </Link>
                </div>
            </div>
        );
    }

    const plan = roadmap.plan;
    const weeks = plan?.weeks || [];

    return (
        <div className="container study-board">
            {/* Breadcrumb */}
            <div className="breadcrumb animate-fadeIn">
                <Link to="/">Courses</Link>
                <span className="separator">/</span>
                <Link to={`/course/${courseId}`}>{course?.name || 'Course'}</Link>
                <span className="separator">/</span>
                <span>Study Plan</span>
            </div>

            {/* Header */}
            <div className="study-header animate-slideUp">
                <div className="header-info">
                    <h1>📖 Study Plan</h1>
                    <p>{plan?.summary}</p>
                </div>
                <div className="header-meta">
                    <div className="meta-item">
                        <span className="meta-label">Goal Date</span>
                        <span className="meta-value">{plan?.goal_date}</span>
                    </div>
                    <div className="meta-item">
                        <span className="meta-label">Hours/Week</span>
                        <span className="meta-value">{plan?.hours_per_week}h</span>
                    </div>
                    <div className="meta-item">
                        <span className="meta-label">Duration</span>
                        <span className="meta-value">{plan?.total_weeks} weeks</span>
                    </div>
                </div>
            </div>

            {/* Timeline */}
            <div className="timeline animate-slideUp" style={{ animationDelay: '100ms' }}>
                {weeks.map((week, index) => {
                    const isExpanded = expandedWeek === index;
                    const isPast = new Date(week.end_date) < new Date();
                    const isCurrent = new Date(week.start_date) <= new Date() &&
                        new Date(week.end_date) >= new Date();

                    return (
                        <div
                            key={index}
                            className={`week-card card ${isExpanded ? 'expanded' : ''} ${isPast ? 'past' : ''} ${isCurrent ? 'current' : ''}`}
                        >
                            <div
                                className="week-header"
                                onClick={() => setExpandedWeek(isExpanded ? null : index)}
                            >
                                <div className="week-info">
                                    <div className="week-number">
                                        {isCurrent && <span className="current-badge">Current</span>}
                                        Week {week.week_number}
                                    </div>
                                    <div className="week-dates">
                                        {week.start_date} → {week.end_date}
                                    </div>
                                </div>

                                <div className="week-topics">
                                    {week.focus_topics?.slice(0, 2).map((topic, i) => (
                                        <span key={i} className="topic-tag">{topic}</span>
                                    ))}
                                    {week.focus_topics?.length > 2 && (
                                        <span className="topic-more">+{week.focus_topics.length - 2}</span>
                                    )}
                                </div>

                                <div className="week-hours">
                                    {week.total_hours}h
                                </div>

                                <span className={`expand-icon ${isExpanded ? 'rotated' : ''}`}>▼</span>
                            </div>

                            {isExpanded && (
                                <div className="week-content">
                                    {/* AI Reflection Note */}
                                    {week.reflection && (
                                        <div className="ai-reflection-note">
                                            {week.reflection}
                                        </div>
                                    )}

                                    {/* Sessions */}
                                    <div className="sessions-grid">
                                        {week.sessions?.map((session, sIndex) => (
                                            <div key={sIndex} className="session-card">
                                                <div className="session-header">
                                                    <h4>{session.topic_name}</h4>
                                                    <span className={`priority-badge ${session.priority}`}>
                                                        {session.priority}
                                                    </span>
                                                </div>
                                                <div className="session-time">
                                                    ⏱️ {session.duration_hours}h study time
                                                </div>

                                                {session.activities && (
                                                    <div className="session-activities">
                                                        <h5>Activities:</h5>
                                                        <ul>
                                                            {session.activities.map((act, aIndex) => (
                                                                <li key={aIndex}>{act}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>

                                    {/* Milestones */}
                                    {week.milestones?.length > 0 && (
                                        <div className="milestones">
                                            <h5>🎯 Milestones</h5>
                                            {week.milestones.map((m, mIndex) => (
                                                <div key={mIndex} className="milestone">{m}</div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Quiz Recommendation */}
                                    {week.quiz_recommended && (
                                        <div className="quiz-rec">
                                            <span>🧠 Quiz recommended this week</span>
                                            <Link to={`/course/${courseId}/quiz`} className="btn btn-secondary btn-sm">
                                                Take Quiz
                                            </Link>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default StudyBoard;
