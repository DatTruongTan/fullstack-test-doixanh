import axios from 'axios';
import type { Task, TaskCreate, UserLogin, UserRegister, AuthResponse } from '../types';
import type { ToastType } from '../contexts/ToastContext';

const API_URL = import.meta.env.VITE_API_URL;

export const api = axios.create({
    baseURL: `${API_URL}/api/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
});

let logoutHandler: (() => void) | null = null;
let showToast: ((message: string, type: ToastType, duration?: number) => void) | null = null;

export const setLogoutHandler = (handler: () => void) => {
    logoutHandler = handler;
};

export const setToastHandler = (handler: (message: string, type: ToastType, duration?: number) => void) => {
    showToast = handler;
};

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            const isLoginEndpoint = error.config.url &&
                (error.config.url.includes('/auth/token') ||
                    error.config.url.includes('/auth/login'));

            if (!isLoginEndpoint) {
                if (showToast) {
                    showToast('Your session has expired. Please log in again.', 'warning');
                }

                localStorage.removeItem('token');
                localStorage.removeItem('username');

                if (logoutHandler) {
                    logoutHandler();
                } else {
                    window.location.href = '/';
                }
            }
        }
        return Promise.reject(error);
    }
);

export const authAPI = {
    login: async (data: UserLogin): Promise<AuthResponse> => {
        const formData = new FormData();
        formData.append('username', data.username);
        formData.append('password', data.password);

        const response = await axios.post<AuthResponse>(`${API_URL}/api/v1/auth/token`, formData);
        return response.data;
    },
    register: async (data: UserRegister) => {
        const response = await api.post('/auth/register', data);
        return response.data;
    },
};

export const taskAPI = {
    getTasks: async (): Promise<Task[]> => {
        const response = await api.get<Task[]>('/tasks');
        return response.data;
    },
    getTask: async (id: number): Promise<Task> => {
        const response = await api.get<Task>(`/tasks/${id}`);
        return response.data;
    },
    createTask: async (task: TaskCreate): Promise<Task> => {
        const response = await api.post<Task>('/tasks', task);
        return response.data;
    },
    updateTask: async (id: number, task: TaskCreate): Promise<Task> => {
        const { id: taskId, owner_id, created_at, ...updateData } = task as any;

        const response = await api.put<Task>(`/tasks/${id}`, updateData);
        return response.data;
    },
    deleteTask: async (id: number): Promise<void> => {
        await api.delete(`/tasks/${id}`);
    },
    searchTasks: async (query: string): Promise<Task[]> => {
        const response = await api.get<Task[]>(`/tasks/search/?query=${query}`);
        return response.data;
    },
}; 