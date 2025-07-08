import { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authAPI } from '../api';
import { setLogoutHandler, setToastHandler } from '../api';
import { useToast } from './ToastContext';
import type { UserLogin, UserRegister } from '../types';

interface User {
    username: string;
}

interface AuthState {
    isAuthenticated: boolean;
    user: User | null;
    loading: boolean;
    error: string | null;
}

type AuthAction =
    | { type: 'AUTH_START' }
    | { type: 'AUTH_SUCCESS'; payload: { user: User } }
    | { type: 'AUTH_FAILURE'; payload: { error: string } }
    | { type: 'AUTH_LOGOUT' }
    | { type: 'AUTH_RESET_ERROR' };

const initialState: AuthState = {
    isAuthenticated: false,
    user: null,
    loading: true,
    error: null
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
    switch (action.type) {
        case 'AUTH_START':
            return {
                ...state,
                loading: true,
                error: null
            };
        case 'AUTH_SUCCESS':
            return {
                ...state,
                isAuthenticated: true,
                user: action.payload.user,
                loading: false,
                error: null
            };
        case 'AUTH_FAILURE':
            return {
                ...state,
                isAuthenticated: false,
                loading: false,
                error: action.payload.error
            };
        case 'AUTH_LOGOUT':
            return {
                ...state,
                isAuthenticated: false,
                user: null,
                error: null
            };
        case 'AUTH_RESET_ERROR':
            return {
                ...state,
                error: null
            };
        default:
            return state;
    }
}

interface AuthContextType {
    isAuthenticated: boolean;
    user: User | null;
    login: (data: UserLogin) => Promise<void>;
    register: (data: UserRegister) => Promise<void>;
    logout: () => void;
    loading: boolean;
    error: string | null;
    resetError: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [state, dispatch] = useReducer(authReducer, initialState);
    const { addToast } = useToast();

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        dispatch({ type: 'AUTH_LOGOUT' });
    };

    useEffect(() => {
        setLogoutHandler(logout);
        setToastHandler(addToast);
    }, [addToast]);

    useEffect(() => {
        const token = localStorage.getItem('token');
        const username = localStorage.getItem('username');

        if (token && username) {
            dispatch({
                type: 'AUTH_SUCCESS',
                payload: { user: { username } }
            });
        } else {
            dispatch({ type: 'AUTH_FAILURE', payload: { error: null as unknown as string } });
        }
    }, []);

    const login = async (data: UserLogin) => {
        try {
            dispatch({ type: 'AUTH_START' });
            const response = await authAPI.login(data);

            localStorage.setItem('token', response.access_token);
            localStorage.setItem('username', data.username);

            dispatch({
                type: 'AUTH_SUCCESS',
                payload: { user: { username: data.username } }
            });
        } catch (err) {
            dispatch({
                type: 'AUTH_FAILURE',
                payload: { error: 'Login failed: Invalid username or password' }
            });
            throw err;
        }
    };

    const register = async (data: UserRegister) => {
        try {
            dispatch({ type: 'AUTH_START' });
            await authAPI.register(data);

            await login({ username: data.username, password: data.password });
        } catch (err) {
            dispatch({
                type: 'AUTH_FAILURE',
                payload: { error: 'Registration failed: Email or username may already be in use' }
            });
            throw err;
        }
    };

    const resetError = () => {
        dispatch({ type: 'AUTH_RESET_ERROR' });
    };

    const value = {
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        login,
        register,
        logout,
        loading: state.loading,
        error: state.error,
        resetError
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 