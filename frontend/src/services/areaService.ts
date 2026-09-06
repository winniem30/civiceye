import api from './api';
import type { Area, Bounds } from '../types';

export const areaService = {
  async createArea(data: { name: string; description?: string; bounds: Bounds }): Promise<Area> {
    const response = await api.post('/areas/', data);
    return response.data;
  },

  async listAreas(skip = 0, limit = 100): Promise<Area[]> {
    const response = await api.get(`/areas/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async getArea(id: number): Promise<Area> {
    const response = await api.get(`/areas/${id}`);
    return response.data;
  },

  async deleteArea(id: number): Promise<void> {
    await api.delete(`/areas/${id}`);
  },
};
