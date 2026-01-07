import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authApi } from '../services/api';
import './Navbar.css';

function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();
    const user = authApi.getUser();

    const handleLogout = () => {
        authApi.logout();
        navigate('/login');
    };

    const isActive = (path) => {
        if (path === '/') return location.pathname === '/';
        return location.pathname.startsWith(path);
    };

    return (
        <nav className="navbar">
            <div className="container navbar-content">
                <Link to="/" className="navbar-brand">
                    <div className="brand-logo-wrapper">
                        <svg className="brand-logo-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 4C12 4 14.5 9 19 9C21.5 9 22.5 7.5 22.5 7.5C22.5 7.5 21.5 18 19 18C14.5 18 12 13 12 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M12 4C12 4 9.5 9 5 9C2.5 9 1.5 7.5 1.5 7.5C1.5 7.5 2.5 18 5 18C9.5 18 12 13 12 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M12 13V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <span className="brand-text">Study Pilot</span>
                    <span className="brand-badge">AI</span>
                </Link>

                <div className="navbar-links">
                    <Link
                        to="/"
                        className={`nav-link ${isActive('/') && location.pathname === '/' ? 'active' : ''}`}
                    >
                        <span className="nav-icon">📚</span>
                        Courses
                    </Link>
                    <Link
                        to="/progress"
                        className={`nav-link ${isActive('/progress') ? 'active' : ''}`}
                    >
                        <span className="nav-icon">📊</span>
                        Progress
                    </Link>
                    <Link
                        to="/ask"
                        className={`nav-link ${isActive('/ask') ? 'active' : ''}`}
                    >
                        <span className="nav-icon">💬</span>
                        Ask AI
                    </Link>
                </div>

                <div className="navbar-user">
                    <div className="user-info">
                        <span className="user-avatar">
                            {user?.name?.charAt(0).toUpperCase() || '?'}
                        </span>
                        <span className="user-name">{user?.name || 'Student'}</span>
                    </div>
                    <button onClick={handleLogout} className="btn btn-ghost btn-sm">
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
