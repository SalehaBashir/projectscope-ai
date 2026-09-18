export interface Project {
  id: string;
  title: string;
  description: string;
  budget?: string | null;
  platform?: string | null;
  status: string;
  created_at: string;
}

export interface Requirement {
  id: string;
  category: string;
  description: string;
}

export interface Feature {
  id: string;
  canonical_name: string;
  description: string;
  priority: string;
  complexity: string;
  confidence: number;
}

export interface AnalysisResult {
  project_type: string;
  users: string[];
  assumptions: string[];
  missing_information: string[];
  requirements: Requirement[];
  features: Feature[];
}

export interface Question {
  id: string;
  category: string;
  description: string;
  [key: string]: unknown;
}

export interface TaskItem {
  id: string;
  title: string;
  role_id: string;
  base_hours: number;
  role_name?: string;
  role_rate?: number;
  feature_name?: string;
}

export interface Risk {
  id: string;
  description: string;
  probability: string;
  impact: string;
  mitigation: string;
  category: string;
  severity: string;
  risk_score: number;
}

export interface EstimateResult {
  min_hours: number;
  expected_hours: number;
  max_hours: number;
  ml_predicted_hours?: number;
  hybrid_expected_hours?: number;
  llm_estimated_hours?: number;
  confidence?: number;
  estimator_version?: string;
  reconciliation_policy?: string;
  complexity_score: number;
  complexity_explanation?: string;
  estimation_explanation?: string;
  min_cost: number;
  expected_cost: number;
  max_cost: number;
  timeline_weeks_min?: number;
  timeline_weeks_expected: number;
  timeline_weeks_max?: number;
  task_count: number;
  schedule?: unknown;
}

export interface Theme {
  id: string;
  name: string;
  primary_color: string;
  secondary_color: string;
  font: string;
  description: string;
}

export interface TechStackRecommendation {
  frontend: string;
  backend: string;
  database: string;
  hosting: string;
  reasoning: string;
}

export interface TechStackResult {
  tech_stack: TechStackRecommendation;
  folder_structure: string[];
  guidelines: string[];
}

export interface MvpFeature {
  id: string;
  canonical_name: string;
  description: string;
  priority: string;
  complexity: string;
}

export interface MvpResult {
  project_id: string;
  recommendation_possible: boolean;
  mvp_features: MvpFeature[];
  phase_2_features: MvpFeature[];
  later_features: MvpFeature[];
  reasoning: string;
  estimated_hours_range: { min: number; expected: number; max: number } | null;
}

export interface FeedbackItem {
  id: string;
  project_id: string;
  user_id?: string | null;
  task_id?: string | null;
  estimated_hours?: number | null;
  actual_hours: number;
  notes?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface FeedbackSummary {
  project_id: string;
  total_feedback_count: number;
  total_estimated_hours?: number | null;
  total_actual_hours: number;
  average_deviation_percent?: number | null;
}
