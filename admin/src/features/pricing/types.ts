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

export interface AiModelWithPrice {
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
  prices: ModelPrice[]
}

export interface ModelsResponse {
  items: AiModelWithPrice[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface ModelHistoryResponse {
  model: AiModelWithPrice
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
