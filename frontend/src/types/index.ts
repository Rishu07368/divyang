// Dashboard Data Types
export interface DashboardSummary {
  total_beneficiaries: number;
  last_updated: string;
  by_gender: Record<string, number>;
  by_age_group: Record<string, number>;
  by_social_status: Record<string, number>;
}

export interface DashboardData {
  summary: DashboardSummary;
  disability_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  village_distribution: Record<string, number>;
  key_metrics: {
    severity_avg_score: number;
    welfare_eligible_total: number;
    without_ayushman: number;
    not_in_school: number;
    high_priority_beneficiaries: number;
  };
  resource_needs: {
    staff: {
      special_educators: number;
      physiotherapists: number;
      speech_therapists: number;
      cbr_workers: number;
    };
  };
  top_insights: InsightSummary[];
}

export interface InsightSummary {
  id: string;
  title: string;
  urgency: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  impact: number;
}

export interface Insight {
  id: string;
  category: string;
  title: string;
  description: string;
  evidence: string[];
  impact_score: number;
  confidence: number;
  urgency: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  recommendations: string[];
  affected_count: number;
  location: string;
}

// Beneficiary Types
export interface Beneficiary {
  unique_id: string;
  child_name: string;
  age: number;
  gender: string;
  disability_type: string;
  disability_degree: string;
  village: string;
  gram_panchayat: string;
  block: string;
  assessment_date: string;
}

export interface SeverityAssessment {
  unique_id: string;
  child_name: string;
  original_degree: string;
  inferred_level: string;
  severity_score: number;
  confidence: number;
  severity_factors: string;
  severity_reasoning: string;
  severity_recommendations: string;
}

export interface WelfareRecommendation {
  unique_id: string;
  child_name: string;
  disability_type: string;
  disability_degree: string;
  primary_scheme: string;
  total_eligible: number;
  has_aadhaar: string;
  has_ayushman: string;
  in_school: string;
}

export interface InterventionZone {
  zone_id: string;
  name: string;
  beneficiary_count: number;
  priority_score: number;
  severity_distribution: Record<string, number>;
  recommended_interventions: string[];
  estimated_cost: number;
  impact_potential: string;
}

export interface CampLocation {
  location_name: string;
  village: string;
  total_beneficiaries: number;
  nearby_villages: string[];
  services_needed: string[];
  recommended_team: string[];
  priority: number;
}

export interface GeoBeneficiary {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number];
  };
  properties: {
    id: string;
    name: string;
    age: number;
    gender: string;
    disability_type: string;
    disability_degree: string;
    village: string;
  };
}

export interface GeoJSON {
  type: 'FeatureCollection';
  features: GeoBeneficiary[];
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  records_processed?: number;
}
