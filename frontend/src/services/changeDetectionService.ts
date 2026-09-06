import api from './api';
import type { ChangeEvent } from '../types';

export const changeDetectionService = {
  async detectChange(data: {
    image_t1_id: number;
    image_t2_id: number;
    area_id?: number;
    method?: string;
  }): Promise<ChangeEvent> {
    const response = await api.post('/change-detection/detect', data);
    return response.data;
  },

  async listChangeEvents(skip = 0, limit = 100): Promise<ChangeEvent[]> {
    const response = await api.get(`/change-detection/events?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async getChangeEvent(id: number): Promise<ChangeEvent> {
    const response = await api.get(`/change-detection/events/${id}`);
    return response.data;
  },
};
