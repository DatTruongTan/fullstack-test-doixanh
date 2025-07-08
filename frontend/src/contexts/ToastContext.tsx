import { createContext, useContext, useReducer } from 'react';
import type { ReactNode } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
    id: string;
    message: string;
    type: ToastType;
    duration?: number;
}

interface ToastState {
    toasts: Toast[];
}

type ToastAction =
    | { type: 'ADD_TOAST'; payload: Toast }
    | { type: 'REMOVE_TOAST'; payload: { id: string } };

const initialState: ToastState = {
    toasts: [],
};

function toastReducer(state: ToastState, action: ToastAction): ToastState {
    switch (action.type) {
        case 'ADD_TOAST':
            return {
                ...state,
                toasts: [...state.toasts, action.payload],
            };
        case 'REMOVE_TOAST':
            return {
                ...state,
                toasts: state.toasts.filter((toast) => toast.id !== action.payload.id),
            };
        default:
            return state;
    }
}

interface ToastContextValue {
    toasts: Toast[];
    addToast: (message: string, type: ToastType, duration?: number) => void;
    removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
    const [state, dispatch] = useReducer(toastReducer, initialState);

    const generateId = () => `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    const addToast = (message: string, type: ToastType = 'info', duration = 5000) => {
        const id = generateId();
        const toast = { id, message, type, duration };

        dispatch({ type: 'ADD_TOAST', payload: toast });

        if (duration > 0) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }
    };

    const removeToast = (id: string) => {
        dispatch({ type: 'REMOVE_TOAST', payload: { id } });
    };

    return (
        <ToastContext.Provider value={{ toasts: state.toasts, addToast, removeToast }}>
            {children}
        </ToastContext.Provider>
    );
}

export function useToast() {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
} 