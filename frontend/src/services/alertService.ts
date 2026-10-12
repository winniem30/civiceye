import api from './api';
import type { Alert } from '../types';

export const alertService = {
  async generateAlert(data: {
    change_event_id: number;
    alert_type?: string;
    title?: string;
    description?: string;
  }): Promise<Alert> {
    const response = await api.post('/alerts/generate', data);
    return response.data;
  },

  async listAlerts(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    severity?: string;
  }): Promise<Alert[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.severity) queryParams.append('severity', params.severity);

    const response = await api.get(`/alerts/list?${queryParams.toString()}`);
    return response.data;
  },

  async getAlert(id: number): Promise<Alert> {
    const response = await api.get(`/alerts/${id}`);
    return response.data;
  },

  async updateAlertStatus(id: number, status: string): Promise<Alert> {
    const response = await api.put(`/alerts/${id}/status`, null, {
      params: { status }
    });
    return response.data;
  },
};
