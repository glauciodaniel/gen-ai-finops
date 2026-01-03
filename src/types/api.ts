export interface OracleRequest {
  question: string;
  n_results?: number;
}

export interface OracleResponse {
  status: string;
  question: string;
  answer: string;
  context_used?: number;
}

export interface ArchitectRequest {
  use_case_description: string;
  monthly_input_tokens: number;
  monthly_output_tokens?: number;
  current_model?: string;
}

export interface ModelRecommendation {
  model: string;
  monthly_cost: string;
  monthly_cost_raw: number;
  reasoning: string;
  action?: string;
}

export interface AlternativeModel {
  provider: string;
  model_name: string;
  monthly_cost: string;
  monthly_cost_raw: number;
  input_cost_per_1m: string;
  output_cost_per_1m: string;
  match_score: number;
  reasons: string[];
  context_window?: number;
  supports_function_calling?: boolean;
  supports_vision?: boolean;
}

export interface SavingsDetails {
  monthly: string;
  monthly_raw: number;
  annual: string;
  annual_raw: number;
  percentage: string;
}

export interface ArchitectResponse {
  status: string;
  use_case: string;
  requirements: Record<string, any>;
  recommendation: ModelRecommendation;
  alternatives: AlternativeModel[];
  volume: {
    monthly_input_tokens: number;
    monthly_output_tokens: number;
  };
  current_model?: {
    name: string;
    monthly_cost: string;
    monthly_cost_raw: number;
  };
  savings?: SavingsDetails;
  message?: string;
}

export interface ScraperStatusResponse {
  status: string;
  total_models: number;
  providers: string[];
  last_updated?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  knowledge_base_status: string;
  llm_available: boolean;
}

export interface StatsResponse {
  status: string;
  total_models: number;
  providers: string[];
  provider_counts: Record<string, number>;
}
