import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor za dodavanje tokena
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor za refresh tokena
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  getMe: () => api.get('/me'),
  updateProfile: (data) => api.patch('/users/me', data),
  deleteAccount: () => api.delete('/users/me'),
};

// Dogs API
export const dogsAPI = {
  getAll: (params) => api.get('/dogs', { params }),
  getById: (id) => api.get(`/dogs/${id}`),
  create: (data) => api.post('/dogs', data),
  update: (id, data) => api.put(`/dogs/${id}`, data),
  delete: (id) => api.delete(`/dogs/${id}`),
  uploadImage: (id, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/dogs/${id}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getImages: (id) => api.get(`/dogs/${id}/images`),
  markPickedUp: (id) => api.post(`/dogs/${id}/picked-up`),
};

// Admin API
export const adminAPI = {
  getPendingDogs: () => api.get('/admin/dogs/pending'),
  confirmRescue: (id) => api.post(`/admin/dogs/${id}/confirm`),
  rejectRescue: (id) => api.post(`/admin/dogs/${id}/reject`),
  updateUserRole: (id, isAdmin) => api.patch(`/admin/users/${id}/role?is_admin=${isAdmin}`),
  deleteImage: (imageId) => api.delete(`/admin/dog-images/${imageId}`),
};

export default api;
