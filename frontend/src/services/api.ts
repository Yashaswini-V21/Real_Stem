import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getNews = (category?: string) => apiClient.get('/news', { params: { category } });
export const getLessons = (topic?: string, level?: number) =>
  apiClient.get('/lessons', { params: { topic, level } });
export const getLesson = (lessonId: string) => apiClient.get(`/lessons/${lessonId}`);
export const getUserProfile = (userId: string) => apiClient.get(`/users/profile/${userId}`);
export const getAnalytics = (userId: string) => apiClient.get(`/analytics/dashboard/${userId}`);

export default apiClient;
