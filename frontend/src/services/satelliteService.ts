import api from './api';
import type { SatelliteImage, Bounds } from '../types';

export const satelliteService = {
  async searchImages(data: {
    bounds: Bounds;
    start_date?: string;
    end_date?: string;
    max_cloud_cover?: number;
    satellite?: string;
  }): Promise<SatelliteImage[]> {
    const response = await api.post('/satellite/search', data);
    return response.data;
  },

  async listImages(skip = 0, limit = 100): Promise<SatelliteImage[]> {
    const response = await api.get(`/satellite/images?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async getImage(id: number): Promise<SatelliteImage> {
    const response = await api.get(`/satellite/images/${id}`);
    return response.data;
  },
};
