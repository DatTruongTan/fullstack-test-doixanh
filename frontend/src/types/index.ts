export interface Task {
    id: number;
    title: string;
    description: string;
    completed: boolean;
    created_at: string;
    due_date: string;
    priority: 'low' | 'normal' | 'high';
    owner_id: number;
}

export interface TaskCreate {
    title: string;
    description?: string;
    completed?: boolean;
    due_date?: string;
    priority?: 'low' | 'normal' | 'high';
}

export interface User {
    id: number;
    email: string;
    username: string;
    is_active: boolean;
    role: string;
}

export interface UserRegister {
    email: string;
    username: string;
    password: string;
}

export interface UserLogin {
    username: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
} 