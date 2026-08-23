const API_BASE = 'https://sih-pm-internship-allocation.onrender.com/api';

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
}

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      method: options.method || 'GET',
      headers,
    };

    if (options.body) {
      config.body = JSON.stringify(options.body);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint);
  }

  async post<T>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body });
  }

  async put<T>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  async uploadFile(endpoint: string, file: File): Promise<any> {
    const token = this.getToken();
    const formData = new FormData();
    formData.append('file', file);

    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }
}

export const api = new ApiClient();

// ==================== AUTH ====================
export const authApi = {
  register: (data: { name: string; email: string; password: string; role: string }) =>
    api.post<any>('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post<any>('/auth/login', data),
  getMe: () => api.get<any>('/auth/me'),
  logout: () => api.post('/auth/logout'),
};

// ==================== STUDENTS ====================
export const studentApi = {
  getProfile: () => api.get<any>('/students/profile'),
  updateProfile: (data: any) => api.put<any>('/students/profile', data),
  addSkill: (data: { name: string; proficiency_level: string }) =>
    api.post<any>('/students/skills', data),
  removeSkill: (skillId: number) => api.delete(`/students/skills/${skillId}`),
  uploadResume: (file: File) => api.uploadFile('/students/resume', file),
  getRecommendations: () => api.get<any[]>('/students/recommendations'),
  getApplications: () => api.get<any[]>('/students/applications'),
  getAllocations: () => api.get<any[]>('/students/allocations'),
  acceptAllocation: (id: number) => api.post(`/students/allocations/${id}/accept`),
  rejectAllocation: (id: number) => api.post(`/students/allocations/${id}/reject`),
};

// ==================== COMPANIES ====================
export const companyApi = {
  getProfile: () => api.get<any>('/companies/profile'),
  updateProfile: (data: any) => api.put<any>('/companies/profile', data),
  createInternship: (data: any) => api.post<any>('/companies/internships', data),
  getInternships: () => api.get<any[]>('/companies/internships'),
  getInternship: (id: number) => api.get<any>(`/companies/internships/${id}`),
  updateInternship: (id: number, data: any) => api.put<any>(`/companies/internships/${id}`, data),
  deleteInternship: (id: number) => api.delete(`/companies/internships/${id}`),
  getApplications: (internshipId: number) =>
    api.get<any[]>(`/companies/internships/${internshipId}/applications`),
  getCandidates: () => api.get<any[]>('/companies/candidates'),
};

// ==================== INTERNSHIPS ====================
export const internshipApi = {
  list: (params?: string) => api.get<any[]>(`/internships${params ? `?${params}` : ''}`),
  search: (q: string) => api.get<any[]>(`/internships/search?q=${encodeURIComponent(q)}`),
  get: (id: number) => api.get<any>(`/internships/${id}`),
  apply: (id: number) => api.post(`/internships/${id}/apply`),
};

// ==================== ADMIN ====================
export const adminApi = {
  getDashboard: () => api.get<any>('/admin/dashboard'),
  getStudents: (params?: string) => api.get<any>(`/admin/students${params ? `?${params}` : ''}`),
  getCompanies: (params?: string) => api.get<any>(`/admin/companies${params ? `?${params}` : ''}`),
  getInternships: (params?: string) => api.get<any>(`/admin/internships${params ? `?${params}` : ''}`),
  getApplications: (params?: string) => api.get<any>(`/admin/applications${params ? `?${params}` : ''}`),
  verifyCompany: (id: number, action: string) =>
    api.post(`/admin/companies/${id}/verify?action=${action}`),
  runAllocation: (config?: any) => api.post<any>('/admin/allocation/run', config),
  getAllocationResults: () => api.get<any[]>('/admin/allocation/results'),
  getAllocationStats: () => api.get<any>('/admin/allocation/statistics'),
  getUnallocatedStudents: () => api.get<any[]>('/admin/allocation/unallocated-students'),
  getUnfilledInternships: () => api.get<any[]>('/admin/allocation/unfilled-internships'),
  getAuditLogs: (params?: string) => api.get<any>(`/admin/audit-logs${params ? `?${params}` : ''}`),
};

// ==================== AI ====================
export const aiApi = {
  computeMatches: (studentId: number) => api.post(`/ai/match/student/${studentId}`),
  getRecommendations: (studentId: number) => api.get<any[]>(`/ai/recommendations/${studentId}`),
  getMatchDetail: (studentId: number, internshipId: number) =>
    api.get<any>(`/ai/match/${studentId}/${internshipId}`),
};

// ==================== NOTIFICATIONS ====================
export const notificationApi = {
  list: () => api.get<any[]>('/notifications'),
  markRead: (id: number) => api.post(`/notifications/${id}/read`),
  markAllRead: () => api.post('/notifications/read-all'),
};
