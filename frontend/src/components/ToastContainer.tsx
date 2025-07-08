import { useToast } from '../contexts/ToastContext';
import type { Toast as ToastType } from '../contexts/ToastContext';
import '../styles/Toast.css';

const Toast = ({ toast, onClose }: { toast: ToastType, onClose: () => void }) => {
    return (
        <div className={`toast toast-${toast.type}`}>
            <div className="toast-content">
                <span className="toast-icon">
                    {toast.type === 'success' && '✅'}
                    {toast.type === 'error' && '❌'}
                    {toast.type === 'warning' && '⚠️'}
                    {toast.type === 'info' && 'ℹ️'}
                </span>
                <span className="toast-message">{toast.message}</span>
            </div>
            <button className="toast-close" onClick={onClose}>×</button>
        </div>
    );
};

export const ToastContainer = () => {
    const { toasts, removeToast } = useToast();

    return (
        <div className="toast-container">
            {toasts.map((toast) => (
                <Toast key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
            ))}
        </div>
    );
}; 