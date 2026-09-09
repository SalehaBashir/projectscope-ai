export type ProjectStatus =
  | 'draft'
  | 'analyzing'
  | 'analyzed'
  | 'estimating'
  | 'completed'

export interface Project {
  id: string
  title: string
  description: string
  budget?: string | null
  platform?: string | null
  project_type?: string | null
  status: ProjectStatus
  created_at: string
  updated_at?: string
}

export type RequirementCategory =
  | 'functional'
  | 'non_functional'
  | 'integration'
  | 'constraint'

export type Priority = 'high' | 'medium' | 'low'
export type Complexity = 'high' | 'medium' | 'low'

export interface Requirement {
  id: string
  project_id?: string
  category: RequirementCategory
  description?: string
  text?: string
  priority?: Priority
  confidence?: number
}

export interface Feature {
  id: string
  project_id?: string
  canonical_name: string
  description: string
  priority: Priority
  complexity: Complexity
}

export interface Question {
  id: string
  project_id?: string
  question: string
  category?: string
  answered: boolean
}

export interface TaskItem {
  id: string
  project_id?: string
  feature_id?: string | null
  title: string
  description?: string
  role: string
  base_hours: number
  is_llm_generated?: boolean
}

export interface RoleEffort {
  role: string
  hours: number
}

export interface Estimate {
  id?: string
  project_id?: string
  min_hours: number
  expected_hours: number
  max_hours: number
  complexity_score: number
  complexity_explanation?: string
  task_count?: number
  min_cost: number
  expected_cost: number
  max_cost: number
  timeline_weeks_min: number
  timeline_weeks_max: number
  timeline_weeks_expected: number
  ml_predicted_hours?: number | null
  hybrid_expected_hours?: number | null
  role_breakdown?: RoleEffort[]
}

export type RiskSeverity = 'high' | 'medium' | 'low'

export interface Risk {
  id: string
  project_id?: string
  description: string
  severity: RiskSeverity
  probability?: number
  impact?: string
  mitigation: string
}

export interface TechStackRecommendation {
  frontend: string
  backend: string
  database: string
  hosting: string
  reasoning: string
}

export interface TechStackResult {
  project_id?: string
  stack: TechStackRecommendation
  folder_structure: string[]
  guidelines: string[]
}

export interface Theme {
  id: string
  name: string
  description: string
  primary_color: string
  secondary_color?: string
  font?: string
}

export interface User {
  id: string
  email: string
  full_name?: string
  organization_name?: string
}