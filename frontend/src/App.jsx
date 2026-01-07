import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { authApi } from './services/api';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import CoursePage from './pages/CoursePage';
import StudyBoard from './pages/StudyBoard';
import QuizPage from './pages/QuizPage';
import ProgressPage from './pages/ProgressPage';
import AskPage from './pages/AskPage';

// Protected Route Component
function ProtectedRoute({ children }) {
    const isAuth = authApi.isAuthenticated();

    if (!isAuth) {
        return <Navigate to="/login" replace />;
    }

    return children;
}

function App() {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Quick auth check on load
        const timer = setTimeout(() => setIsLoading(false), 100);
        return () => clearTimeout(timer);
    }, []);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full" style={{ minHeight: '100vh' }}>
                <div className="text-center">
                    <div className="animate-pulse text-accent" style={{ fontSize: '2rem' }}>⚡</div>
                    <p className="text-secondary mt-md">Loading Study Pilot...</p>
                </div>
            </div>
        );
    }

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage />} />

                <Route path="/*" element={
                    <ProtectedRoute>
                        <div className="flex flex-col h-full" style={{ minHeight: '100vh' }}>
                            <Navbar />
                            <main className="page">
                                <Routes>
                                    <Route path="/" element={<Dashboard />} />
                                    <Route path="/course/:courseId" element={<CoursePage />} />
                                    <Route path="/course/:courseId/study" element={<StudyBoard />} />
                                    <Route path="/course/:courseId/quiz" element={<QuizPage />} />
                                    <Route path="/progress" element={<ProgressPage />} />
                                    <Route path="/ask" element={<AskPage />} />
                                </Routes>
                            </main>
                        </div>
                    </ProtectedRoute>
                } />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
