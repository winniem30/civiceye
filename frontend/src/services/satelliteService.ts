import api from './api';
import type { Bounds } from '../types';

export interface SatelliteImage {
  id: number;
  satellite_name: string;
  stac_id: string;
  acquisition_date: string;
  cloud_cover: number;
  bounds: Bounds;
  metadata: any;
}

export interface Observation {
  id: number;
  stac_id: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  aoi_bounds: Bounds | null;
  band_files: Record<string, string> | null;
  index_files: Record<string, string> | null;
  metadata: any;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export const satelliteService = {
  async searchObservations(data: {
    bounds: Bounds;
    start_date?: string;
    end_date?: string;
    max_cloud_cover?: number;
    satellite?: string;
  }): Promise<SatelliteImage[]> {
    const response = await api.post('/satellite/search', data);
    return response.data;
  },

  async processObservation(data: {
    stac_id: string;
    aoi_bounds?: Bounds;
    clip_to_aoi?: boolean;
  }): Promise<Observation> {
    const response = await api.post('/satellite/process', data);
    return response.data;
  },

  async listObservations(skip = 0, limit = 100, processingStatus?: string): Promise<Observation[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (processingStatus) {
      params.append('processing_status', processingStatus);
    }
    const response = await api.get(`/satellite/observations?${params.toString()}`);
    return response.data;
  },

  async getObservation(observationId: number): Promise<Observation> {
    const response = await api.get(`/satellite/observations/${observationId}`);
    return response.data;
  },

  async getObservationLayers(observationId: number): Promise<{
    observation_id: number;
    stac_id: string;
    bands: Record<string, string>;
    indices: Record<string, string>;
    metadata: any;
  }> {
    const response = await api.get(`/satellite/observations/${observationId}/layers`);
    return response.data;
  },

  async getRasterTile(observationId: number, layerName: string, width = 512, height = 512): Promise<Blob> {
    const response = await api.get(
      `/raster/raster/${observationId}/${layerName}?width=${width}&height=${height}`,
      { responseType: 'blob' }
    );
    return response.data;
  },

  async getRasterMetadata(observationId: number, layerName: string): Promise<any> {
    const response = await api.get(`/raster/raster/${observationId}/${layerName}/metadata`);
    return response.data;
  },
};
