import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import '../styles/LoginPage.css';

const LoginPage = () => {
    const { isAuthenticated, login, register, loading, error, resetError } = useAuth();
    const { addToast } = useToast();

    const [isLoginMode, setIsLoginMode] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');

    const switchMode = () => {
        resetError();
        setIsLoginMode(!isLoginMode);
    };

    useEffect(() => {
        if (error) {
            if (!error.includes('session has expired')) {
                addToast(error, 'error');
            }
            resetError();
        }
    }, [error, addToast, resetError]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!username.trim() || !password.trim() || (!isLoginMode && !email.trim())) {
            addToast('Please fill in all fields', 'warning');
            return;
        }

        try {
            if (isLoginMode) {
                await login({ username, password });
            } else {
                await register({ username, password, email });
            }
        } catch (err) {
            console.error('Authentication error:', err);
        }
    };

    if (isAuthenticated) {
        return <Navigate to="/tasks" />;
    }

    return (
        <div className="login-container">
            <div className="login-form-container">
                <h1>{isLoginMode ? 'Login' : 'Register'}</h1>
                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    {!isLoginMode && (
                        <div className="form-group">
                            <label htmlFor="email">Email</label>
                            <input
                                type="email"
                                id="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                disabled={loading}
                            />
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    <button type="submit" className="submit-button" disabled={loading}>
                        {loading ? 'Loading...' : isLoginMode ? 'Login' : 'Register'}
                    </button>
                </form>

                <div className="mode-switch">
                    <button onClick={switchMode} disabled={loading}>
                        {isLoginMode ? 'Need an account? Register' : 'Already have an account? Login'}
                    </button>
                </div>
            </div>

            <div className="app-info">
                <h2>Task Management App</h2>
                <p>Organize your tasks efficiently with our simple and intuitive task management application.</p>
                <ul>
                    <li>Create and organize tasks</li>
                    <li>Set priorities and due dates</li>
                    <li>Track your progress</li>
                    <li>Simple and clean interface</li>
                </ul>
            </div>
        </div>
    );
};

export default LoginPage; 