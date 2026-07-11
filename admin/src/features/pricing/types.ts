export interface Provider {
  id: number
  slug: string
  name: string
  pricing_url: string | null
}

export interface ModelPrice {
  id: number
  model_id: number
  input_per_1m: string | number
  output_per_1m: string | number
  cached_input_per_1m: string | number | null
  currency: string
  effective_from: string
  source: string
  scrape_run_id: number | null
}

export interface AiModel {
  id: number
  provider_id: number
  slug: string
  display_name: string
  modality: string
  context_window: number | null
  max_output: number | null
  supports_tools: boolean
  supports_vision: boolean
  supports_json: boolean
  deprecated: boolean
  provider: { slug: string; name: string }
}

export interface AiModelWithPrice extends AiModel {
  model_price: ModelPrice[]
}

export interface ModelsResponse {
  items: AiModelWithPrice[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface ModelHistoryResponse {
  model: AiModel
  prices: ModelPrice[]
}

export interface ScrapeRun {
  id: number
  started_at: string
  finished_at: string | null
  status: 'running' | 'success' | 'partial' | 'failed'
  provider: string | null
  items_found: number
  items_changed: number
  error_log: string | null
}

export interface PricingStats {
  providers: number
  activeModels: number
  priceRecords: number
  lastScrapeAt: string | null
  lastScrapeStatus: ScrapeRun['status'] | null
}

export interface OptimizerRequirements {
  requireTools: boolean
  requireVision: boolean
  requireJson: boolean
  minContextWindow: number | null
  qualityTier: 'basic' | 'balanced' | 'premium'
  modality: 'text' | 'embedding' | 'image' | 'audio'
}

export interface OptimizerUsage {
  inputTokensPerRequest: number
  outputTokensPerRequest: number
  monthlyRequests: number
}

export interface OptimizerRecommendation {
  id: number
  slug: string
  displayName: string
  providerSlug: string
  providerName: string
  modality: string
  contextWindow: number | null
  supportsTools: boolean
  supportsVision: boolean
  supportsJson: boolean
  inputPer1M: number
  outputPer1M: number
  cachedInputPer1M: number | null
  score: number
  monthlyCost: number
  reasoning: string[]
}

export interface OptimizerSavings {
  currentModelSlug: string
  currentMonthlyCost: number
  recommendedMonthlyCost: number
  monthlySavings: number
  annualSavings: number
  savingsPercent: number
}

export interface OptimizerResult {
  requirements: OptimizerRequirements
  usage: OptimizerUsage
  recommendations: OptimizerRecommendation[]
  savings: OptimizerSavings | null
  requirementsSource: 'user' | 'llm' | 'heuristic'
}

export interface OptimizerRequest {
  useCase: string
  inputTokensPerRequest?: number
  outputTokensPerRequest?: number
  monthlyRequests?: number
  currentModelSlug?: string
  topN?: number
}
