import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000/api/';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

let refreshPromise = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      originalRequest.url?.includes('auth/login/') ||
      originalRequest.url?.includes('auth/refresh/')
    ) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      clearSession();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = axios.post(
          `${BASE_URL}auth/refresh/`,
          { refresh: refreshToken }
        );
      }

      const response = await refreshPromise;
      const newAccess = response.data.access;

      localStorage.setItem('access_token', newAccess);

      if (response.data.refresh) {
        localStorage.setItem('refresh_token', response.data.refresh);
      }

      originalRequest.headers.Authorization = `Bearer ${newAccess}`;

      return api(originalRequest);
    } catch (refreshError) {
      clearSession();
      return Promise.reject(refreshError);
    } finally {
      refreshPromise = null;
    }
  }
);

function clearSession() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}

export default api;
