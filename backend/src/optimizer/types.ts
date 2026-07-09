export interface Requirements {
  requireTools: boolean;
  requireVision: boolean;
  requireJson: boolean;
  minContextWindow: number | null;
  qualityTier: 'basic' | 'balanced' | 'premium';
  modality: 'text' | 'embedding' | 'image' | 'audio';
}

export interface UsageProfile {
  inputTokensPerRequest: number;
  outputTokensPerRequest: number;
  monthlyRequests: number;
}

export interface CandidateModel {
  id: number;
  slug: string;
  displayName: string;
  providerSlug: string;
  providerName: string;
  modality: string;
  contextWindow: number | null;
  supportsTools: boolean;
  supportsVision: boolean;
  supportsJson: boolean;
  inputPer1M: number;
  outputPer1M: number;
  cachedInputPer1M: number | null;
}

export interface Recommendation extends CandidateModel {
  score: number;
  monthlyCost: number;
  reasoning: string[];
}

export interface SavingsProjection {
  currentModelSlug: string;
  currentMonthlyCost: number;
  recommendedMonthlyCost: number;
  monthlySavings: number;
  annualSavings: number;
  savingsPercent: number;
}

export interface OptimizeResult {
  requirements: Requirements;
  usage: UsageProfile;
  recommendations: Recommendation[];
  savings: SavingsProjection | null;
  requirementsSource: 'user' | 'llm' | 'heuristic';
}
