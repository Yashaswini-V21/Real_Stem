import axios from 'axios';
import { NewsItem } from '../types/news';
import { Lesson } from '../types/lesson';
import { User } from '../types/user';

// --- API Configuration ---

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Request Interceptor ---

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- Response Interceptor ---

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // Using window.location.href for simplicity in a non-component context
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    if (!error.response) {
      console.error('Network Error: Please check your internet connection.');
    }
    
    return Promise.reject(error);
  }
);

// --- Types ---

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  role?: 'student' | 'teacher' | 'admin';
  country?: string;
  language?: string;
  grade_level?: string;
  subjects?: string[];
}

export interface ProfileData {
  full_name?: string;
  bio?: string;
  avatar_url?: string;
  preferences?: Record<string, any>;
}

export interface LessonListResponse {
  items: Lesson[];
  total: number;
}

// --- API Functions ---

export const newsApi = {
  getNews: (params: { limit?: number; offset?: number; stemOnly?: boolean }) =>
    api.get<any, { items: NewsItem[]; total: number }>('/api/news', { params }),
    
  getNewsById: (id: string | number) =>
    api.get<any, NewsItem>(`/api/news/${id}`),
    
  getBreakingNews: () =>
    api.get<any, NewsItem[]>('/api/news/breaking'),
    
  getTrendingNews: () =>
    api.get<any, NewsItem[]>('/api/news/trending'),
};

export const lessonsApi = {
  getLessons: (params: { 
    status?: string; 
    level?: string; 
    subject?: string; 
    limit?: number; 
    offset?: number; 
  }) =>
    api.get<any, LessonListResponse>('/api/lessons', { params }),
    
  getLessonById: (id: string | number) =>
    api.get<any, Lesson>(`/api/lessons/${id}`),
    
  getLessonContent: (id: string | number, level: string) =>
    api.get<any, any>(`/api/lessons/${id}/content/${level}`),
    
  generateLesson: (newsId: string | number, breakingMode: boolean) =>
    api.post<any, any>('/api/lessons/generate', { 
      news_article_id: newsId, 
      breaking_news_mode: breakingMode 
    }),
    
  rateLesson: (id: string | number, rating: number) =>
    api.post<any, any>(`/api/lessons/${id}/rate`, { rating }),
    
  searchLessons: (query: string) =>
    api.get<any, LessonListResponse>('/api/lessons/search', { params: { q: query } }),
};

export const usersApi = {
  register: (data: RegisterData) =>
    api.post<any, User>('/api/users/register', {
      email: data.email,
      password: data.password,
      full_name: data.name,
      role: data.role || 'student',
      country: data.country,
      language: data.language,
      grade_level: data.grade_level,
      subjects: data.subjects
    }),
    
  login: (email: string, password: string) =>
    api.post<any, AuthResponse>('/api/users/login', { username: email, password }),
    
  getCurrentUser: () =>
    api.get<any, User>('/api/users/me'),
    
  updateProfile: (data: ProfileData) =>
    api.put<any, User>('/api/users/me', data),
    
  getProgress: () =>
    api.get<any, any>('/api/users/me/progress'),
    
  getImpact: () =>
    api.get<any, any>('/api/users/me/impact'),
};

export default api;

