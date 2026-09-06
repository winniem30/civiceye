export interface Bounds {
  min_x: number;
  min_y: number;
  max_x: number;
  max_y: number;
}

export interface Area {
  id: number;
  name: string;
  description?: string;
  bounds: Bounds;
  geometry?: any;
}

export interface SatelliteImage {
  id: number;
  satellite_name: string;
  acquisition_date: string;
  cloud_cover?: number;
  bounds: Bounds;
  metadata?: any;
  file_path?: string;
  preview_path?: string;
}

export interface ChangeEvent {
  id: number;
  image_t1_id: number;
  image_t2_id: number;
  change_area: number;
  change_percentage: number;
  confidence: number;
  is_human_induced?: boolean;
  human_confidence?: number;
  activity_type?: string;
  activity_confidence?: number;
  change_mask_path?: string;
  bounding_geometry?: any;
  first_detected: string;
  last_updated: string;
}

export interface ChangeDNA {
  human_activity_probability: number;
  growth_rate: string;
  persistence: string;
  frequency: string;
  environmental_proximity: string;
  historical_activity: string;
}

export interface RiskAssessment {
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  explanation?: string;
  shap_values?: any;
}

export interface Alert {
  id: number;
  alert_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: string;
  title: string;
  description: string;
  location: string;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  role: 'admin' | 'analyst' | 'citizen';
  is_active: boolean;
}
