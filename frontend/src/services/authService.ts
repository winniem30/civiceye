import api from './api';
import type { User } from '../types';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  async register(data: {
    email: string;
    username: string;
    password: string;
    role?: string;
  }): Promise<User> {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('token');
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },
};
