import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import TaskList from '../components/TaskList';

const TasksPage = () => {
    const { isAuthenticated, user, logout } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/" />;
    }

    return (
        <div className="tasks-page">
            <header className="app-header">
                <h1>TodoList App</h1>
                <div className="user-controls">
                    {user && <span>Welcome, {user.username}</span>}
                    <button onClick={logout} className="logout-button">Logout</button>
                </div>
            </header>

            <main className="main-content">
                <TaskList />
            </main>

            <footer className="app-footer">
                <p>&copy; {new Date().getFullYear()} TodoList App</p>
            </footer>
        </div>
    );
};

export default TasksPage; 