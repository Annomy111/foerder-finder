/**
 * Authentication Types
 */

export interface User {
  id: string;
  email: string;
  role: 'admin' | 'lehrkraft' | 'user';
  school_id?: string;
  school_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: 'bearer';
  user: User;
}

export interface RegisterData {
  email: string;
  password: string;
  school_name: string;
  role?: 'admin' | 'lehrkraft';
}

export interface RegisterResponse {
  id: string;
  email: string;
  school_id: string;
  school_name: string;
  role: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}
