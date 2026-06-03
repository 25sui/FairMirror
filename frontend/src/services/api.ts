import axios from 'axios';
import {
  JDAuditResponse,
  ResumeScanResponse,
  InterviewAnalysisResponse,
  ComplianceReport,
  DashboardMetrics,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  register: async (userData: {
    email: string;
    username: string;
    password: string;
    role: string;
  }) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

export const jdAPI = {
  analyze: async (jdText: string, jobTitle?: string): Promise<JDAuditResponse> => {
    const response = await apiClient.post('/jd/analyze', {
      jd_text: jdText,
      job_title: jobTitle,
    });
    return response.data;
  },

  create: async (jobData: any) => {
    const response = await apiClient.post('/jd/', jobData);
    return response.data;
  },

  list: async (companyId?: number) => {
    const response = await apiClient.get('/jd/', {
      params: { company_id: companyId },
    });
    return response.data;
  },

  get: async (jobId: number) => {
    const response = await apiClient.get(`/jd/${jobId}`);
    return response.data;
  },
};

export const resumeAPI = {
  scan: async (resumeText: string, jobId?: number): Promise<ResumeScanResponse> => {
    const response = await apiClient.post('/resume/scan', {
      resume_text: resumeText,
      job_id: jobId,
    });
    return response.data;
  },

  create: async (candidateId: string, content: string, jobId?: number) => {
    const response = await apiClient.post('/resume/', null, {
      params: { candidate_id: candidateId, content, job_id: jobId },
    });
    return response.data;
  },
};

export const interviewAPI = {
  analyze: async (
    interviewData: any[],
    groups?: string[]
  ): Promise<InterviewAnalysisResponse> => {
    const response = await apiClient.post('/interview/analyze', {
      interview_data: interviewData,
      groups,
    });
    return response.data;
  },

  createBatch: async (records: any[]) => {
    const response = await apiClient.post('/interview/batch', records);
    return response.data;
  },

  getByJob: async (jobId: number) => {
    const response = await apiClient.get(`/interview/job/${jobId}`);
    return response.data;
  },
};

export const complianceAPI = {
  getEUAIActReport: async (companyId: number): Promise<ComplianceReport> => {
    const response = await apiClient.get(`/compliance/eu-ai-act/${companyId}`);
    return response.data;
  },

  getChinaAIethicsReport: async (companyId: number): Promise<ComplianceReport> => {
    const response = await apiClient.get(`/compliance/china-ai-ethics/${companyId}`);
    return response.data;
  },

  exportReport: async (companyId: number, regulationType: string) => {
    const response = await apiClient.post('/compliance/report/export', null, {
      params: { company_id: companyId, regulation_type: regulationType },
    });
    return response.data;
  },
};

export const dashboardAPI = {
  getMetrics: async (companyId?: number): Promise<DashboardMetrics> => {
    const response = await apiClient.get('/dashboard/metrics', {
      params: { company_id: companyId },
    });
    return response.data;
  },
};

export default apiClient;
