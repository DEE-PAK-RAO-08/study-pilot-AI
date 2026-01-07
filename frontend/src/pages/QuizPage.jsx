import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { quizApi, coursesApi } from '../services/api';
import './QuizPage.css';

function QuizPage() {
    const { courseId } = useParams();
    const [course, setCourse] = useState(null);
    const [quiz, setQuiz] = useState(null);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [answers, setAnswers] = useState({});
    const [submitted, setSubmitted] = useState(false);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadCourse();
    }, [courseId]);

    const loadCourse = async () => {
        try {
            const data = await coursesApi.getById(courseId);
            setCourse(data);
        } catch (err) {
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    const startQuiz = async (numQuestions = 10) => {
        setLoading(true);
        try {
            const data = await quizApi.generate(courseId, numQuestions);
            setQuiz(data);
            setCurrentIndex(0);
            setAnswers({});
            setSubmitted(false);
            setResults(null);
        } catch (err) {
            console.error('Error generating quiz:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswer = (answer) => {
        setAnswers({ ...answers, [currentIndex]: answer });
    };

    const handleNext = () => {
        if (currentIndex < quiz.questions.length - 1) {
            setCurrentIndex(currentIndex + 1);
        }
    };

    const handlePrev = () => {
        if (currentIndex > 0) {
            setCurrentIndex(currentIndex - 1);
        }
    };

    const handleSubmit = async () => {
        setSubmitting(true);
        try {
            // Convert answers to array
            const responses = quiz.questions.map((_, i) => answers[i] || '');
            const data = await quizApi.submit(quiz.quiz_id, responses);
            setResults(data);
            setSubmitted(true);
        } catch (err) {
            console.error('Error submitting quiz:', err);
            alert('Failed to submit quiz');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="container">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading...</p>
                </div>
            </div>
        );
    }

    // Quiz selection screen
    if (!quiz) {
        return (
            <div className="container quiz-page">
                <div className="breadcrumb animate-fadeIn">
                    <Link to="/">Courses</Link>
                    <span className="separator">/</span>
                    <Link to={`/course/${courseId}`}>{course?.name || 'Course'}</Link>
                    <span className="separator">/</span>
                    <span>Quiz</span>
                </div>

                <div className="quiz-start animate-slideUp">
                    <div className="quiz-start-icon">🧠</div>
                    <h1>Ready to Test Your Knowledge?</h1>
                    <p>Take an adaptive quiz tailored to your mastery level</p>

                    <div className="quiz-options">
                        <button onClick={() => startQuiz(5)} className="quiz-option card interactive">
                            <span className="option-num">5</span>
                            <span className="option-label">Quick Quiz</span>
                            <span className="option-time">~5 minutes</span>
                        </button>
                        <button onClick={() => startQuiz(10)} className="quiz-option card interactive">
                            <span className="option-num">10</span>
                            <span className="option-label">Standard Quiz</span>
                            <span className="option-time">~10 minutes</span>
                        </button>
                        <button onClick={() => startQuiz(20)} className="quiz-option card interactive">
                            <span className="option-num">20</span>
                            <span className="option-label">Full Practice</span>
                            <span className="option-time">~20 minutes</span>
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Results screen
    if (submitted && results) {
        return (
            <div className="container quiz-page">
                <div className="breadcrumb animate-fadeIn">
                    <Link to="/">Courses</Link>
                    <span className="separator">/</span>
                    <Link to={`/course/${courseId}`}>{course?.name || 'Course'}</Link>
                    <span className="separator">/</span>
                    <span>Quiz Results</span>
                </div>

                <div className="results animate-slideUp">
                    <div className="results-header">
                        <div className="score-circle">
                            <span className="score-value">{results.percentage}%</span>
                            <span className="score-label">{results.score}/{results.total} correct</span>
                        </div>
                        <h2>
                            {results.percentage >= 80 ? '🎉 Excellent!' :
                                results.percentage >= 60 ? '👍 Good Job!' :
                                    results.percentage >= 40 ? '📚 Keep Practicing!' :
                                        '💪 You Can Do Better!'}
                        </h2>
                    </div>

                    <div className="results-breakdown">
                        <h3>Topic Breakdown</h3>
                        <div className="topic-results">
                            {Object.entries(results.topic_breakdown || {}).map(([topicId, data]) => (
                                <div key={topicId} className="topic-result">
                                    <div className="topic-result-info">
                                        <span className="topic-result-name">Topic {topicId}</span>
                                        <span className="topic-result-score">
                                            {data.correct}/{data.total} ({data.percentage}%)
                                        </span>
                                    </div>
                                    <div className="progress-bar">
                                        <div
                                            className={`progress-fill ${data.percentage >= 70 ? 'progress-high' :
                                                data.percentage >= 40 ? 'progress-medium' : 'progress-low'}`}
                                            style={{ width: `${data.percentage}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="results-details">
                        <h3>Question Review</h3>
                        {results.results?.map((result, index) => (
                            <div key={index} className={`result-item ${result.correct ? 'correct' : 'incorrect'}`}>
                                <div className="result-header">
                                    <span className="result-num">Q{index + 1}</span>
                                    <span className={`result-badge ${result.correct ? 'correct' : 'incorrect'}`}>
                                        {result.correct ? '✓ Correct' : '✗ Incorrect'}
                                    </span>
                                </div>
                                <p className="result-question">{quiz.questions[index]?.question_text}</p>
                                <div className="result-answer">
                                    <span className="answer-label">Your answer:</span>
                                    <span className="answer-value">{answers[index] || 'Not answered'}</span>
                                </div>
                                {!result.correct && (
                                    <div className="result-correct">
                                        <span className="answer-label">Correct answer:</span>
                                        <span className="answer-value">{result.correct_answer}</span>
                                    </div>
                                )}
                                {result.explanation && (
                                    <p className="result-explanation">{result.explanation}</p>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="results-actions">
                        <button onClick={() => startQuiz(quiz.questions.length)} className="btn btn-primary">
                            Try Again
                        </button>
                        <Link to={`/course/${courseId}`} className="btn btn-secondary">
                            Back to Course
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    // Quiz in progress
    const question = quiz.questions[currentIndex];
    const answeredCount = Object.keys(answers).length;
    const progress = ((currentIndex + 1) / quiz.questions.length) * 100;

    return (
        <div className="container quiz-page">
            {/* Progress Bar */}
            <div className="quiz-progress-bar">
                <div className="quiz-progress-fill" style={{ width: `${progress}%` }}></div>
            </div>

            {/* Quiz Header */}
            <div className="quiz-header animate-fadeIn">
                <span className="quiz-counter">
                    Question {currentIndex + 1} of {quiz.questions.length}
                </span>
                <div className="quiz-meta">
                    {question.topic_name && (
                        <span className="topic-tag">{question.topic_name}</span>
                    )}
                    {question.difficulty && (
                        <span className={`difficulty-badge ${question.difficulty}`}>
                            {question.difficulty}
                        </span>
                    )}
                </div>
            </div>

            {/* Question */}
            <div className="question-card card animate-slideUp" key={currentIndex}>
                <h2 className="question-text">{question.question_text}</h2>

                {question.question_type === 'mcq' && question.options && (
                    <div className="options">
                        {question.options.map((option, idx) => {
                            const letter = String.fromCharCode(65 + idx);
                            const isSelected = answers[currentIndex] === option;

                            return (
                                <button
                                    key={idx}
                                    className={`option ${isSelected ? 'selected' : ''}`}
                                    onClick={() => handleAnswer(option)}
                                >
                                    <span className="option-letter">{letter}</span>
                                    <span className="option-text">{option}</span>
                                </button>
                            );
                        })}
                    </div>
                )}

                {question.question_type === 'true_false' && (
                    <div className="options tf-options">
                        <button
                            className={`option ${answers[currentIndex] === 'true' ? 'selected' : ''}`}
                            onClick={() => handleAnswer('true')}
                        >
                            True
                        </button>
                        <button
                            className={`option ${answers[currentIndex] === 'false' ? 'selected' : ''}`}
                            onClick={() => handleAnswer('false')}
                        >
                            False
                        </button>
                    </div>
                )}
            </div>

            {/* Navigation */}
            <div className="quiz-nav">
                <button
                    onClick={handlePrev}
                    className="btn btn-secondary"
                    disabled={currentIndex === 0}
                >
                    ← Previous
                </button>

                <div className="nav-dots">
                    {quiz.questions.map((_, idx) => (
                        <button
                            key={idx}
                            className={`nav-dot ${idx === currentIndex ? 'current' : ''} ${answers[idx] ? 'answered' : ''}`}
                            onClick={() => setCurrentIndex(idx)}
                        />
                    ))}
                </div>

                {currentIndex === quiz.questions.length - 1 ? (
                    <button
                        onClick={handleSubmit}
                        className="btn btn-primary"
                        disabled={submitting}
                    >
                        {submitting ? 'Submitting...' : `Submit Quiz (${answeredCount}/${quiz.questions.length})`}
                    </button>
                ) : (
                    <button
                        onClick={handleNext}
                        className="btn btn-primary"
                    >
                        Next →
                    </button>
                )}
            </div>
        </div>
    );
}

export default QuizPage;
