import axios from 'axios';
import type { AuthResponse, DataSource, Employee, ETLJob } from '@/types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to include credentials
api.interceptors.request.use((config) => {
  config.withCredentials = true;
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email: string, password: string) =>
    api.post<AuthResponse>('/auth/login', { email, password }),
  
  register: (email: string, password: string) =>
    api.post<AuthResponse>('/auth/register', { email, password }),
  
  logout: () => api.post('/auth/logout'),
  
  me: () => api.get('/auth/me'),
};

export const dataSourceApi = {
  list: () => api.get<{ data_sources: DataSource[] }>('/data-sources/'),
  
  create: (data: Omit<DataSource, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<DataSource>('/data-sources/', data),
  
  get: (id: number) => api.get<DataSource>(`/data-sources/${id}`),
  
  update: (id: number, data: Partial<DataSource>) =>
    api.put<DataSource>(`/data-sources/${id}`, data),
  
  delete: (id: number) => api.delete(`/data-sources/${id}`),
  
  testConnection: (id: number) =>
    api.post(`/data-sources/${id}/test-connection`),
};

export const employeeApi = {
  list: (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    department?: string;
    status?: string;
  }) => api.get<{ employees: Employee[]; pagination: any }>('/employees/', { params }),
  
  get: (id: number) => api.get<Employee>(`/employees/${id}`),
  
  getStats: () => api.get('/employees/stats/summary'),
};

export const etlApi = {
  uploadFile: (file: File, dataSourceId: number) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_source_id', dataSourceId.toString());
    
    return api.post('/etl/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  listJobs: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get<{ jobs: ETLJob[] }>('/etl/jobs', { params }),
  
  getJob: (id: number) => api.get<ETLJob>(`/etl/jobs/${id}`),
  
  startProcessing: (id: number) => api.post(`/etl/jobs/${id}/process`),
  
  getJobStatus: (id: number) => api.get(`/etl/jobs/${id}/status`),
};

export const mappingApi = {
  getMappings: (sourceId: number) => api.get(`/mappings/${sourceId}`),
  
  createMapping: (sourceId: number, mapping: any) => 
    api.post(`/mappings/${sourceId}`, mapping),
  
  updateMapping: (mappingId: number, mapping: any) => 
    api.put(`/mappings/${mappingId}`, mapping),
  
  deleteMapping: (mappingId: number) => api.delete(`/mappings/${mappingId}`),
  
  bulkCreateMappings: (sourceId: number, mappings: any[]) => 
    api.post(`/mappings/${sourceId}/bulk`, mappings),
  
  createTemplate: (template: { name: string; description?: string; mappings: any[] }) => 
    api.post('/mappings/templates', template),
  
  listTemplates: () => api.get('/mappings/templates'),
  
  getTemplate: (templateId: number) => api.get(`/mappings/templates/${templateId}`),
  
  previewMapping: (sourceId: number) => api.get(`/mappings/preview/${sourceId}`),
  
  createDefaultTemplate: (sourceType: string = 'workday') => 
    api.post(`/mappings/templates/default?source_type=${sourceType}`),
  
  createMultiSourceMapping: (mappingData: any) => 
    api.post('/mappings/multi-source', mappingData),
  
  getMultiSourceMapping: (mappingSetId: string) => 
    api.get(`/mappings/multi-source/${mappingSetId}`),
};

export default api;