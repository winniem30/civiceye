import api from './api';
import type { Investigation } from '../types';

export const investigationService = {
  async createInvestigation(data: {
    change_event_id: number;
    user_id: number;
    report?: string;
  }): Promise<Investigation> {
    const response = await api.post('/investigation/create', data);
    return response.data;
  },

  async listInvestigations(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    user_id?: number;
  }): Promise<Investigation[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.user_id) queryParams.append('user_id', params.user_id.toString());

    const response = await api.get(`/investigation/list?${queryParams.toString()}`);
    return response.data;
  },

  async getInvestigation(id: number): Promise<Investigation> {
    const response = await api.get(`/investigation/${id}`);
    return response.data;
  },

  async completeInvestigation(id: number, report: string): Promise<Investigation> {
    const response = await api.put(`/investigation/${id}/complete`, { report });
    return response.data;
  },
};
