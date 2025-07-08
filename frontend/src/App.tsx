import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import LoginPage from './pages/LoginPage';
import TasksPage from './pages/TasksPage';
import { ToastContainer } from './components/ToastContainer';
import './App.css';

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<LoginPage />} />
            <Route path="/tasks" element={<TasksPage />} />
          </Routes>
        </Router>
        <ToastContainer />
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
