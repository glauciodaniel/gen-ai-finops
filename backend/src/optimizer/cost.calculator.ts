import type { CandidateModel, UsageProfile, SavingsProjection } from './types';

/**
 * Monthly cost from usage + per-1M prices. Pure arithmetic:
 *   cost = requests * (inputTokens/1M * inputPrice + outputTokens/1M * outputPrice)
 *
 * All prices are USD per 1M tokens (matching the DB schema).
 */
export function calculateMonthlyCost(
  usage: UsageProfile,
  inputPer1M: number,
  outputPer1M: number,
): number {
  const perRequest =
    (usage.inputTokensPerRequest / 1_000_000) * inputPer1M +
    (usage.outputTokensPerRequest / 1_000_000) * outputPer1M;
  return round2(perRequest * usage.monthlyRequests);
}

export function costForCandidate(
  usage: UsageProfile,
  candidate: CandidateModel,
): number {
  return calculateMonthlyCost(usage, candidate.inputPer1M, candidate.outputPer1M);
}

export function projectSavings(
  usage: UsageProfile,
  current: CandidateModel,
  recommended: CandidateModel,
): SavingsProjection {
  const currentCost = costForCandidate(usage, current);
  const recommendedCost = costForCandidate(usage, recommended);
  const monthlySavings = round2(currentCost - recommendedCost);
  const savingsPercent =
    currentCost > 0 ? round2((monthlySavings / currentCost) * 100) : 0;
  return {
    currentModelSlug: current.slug,
    currentMonthlyCost: currentCost,
    recommendedMonthlyCost: recommendedCost,
    monthlySavings,
    annualSavings: round2(monthlySavings * 12),
    savingsPercent,
  };
}

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}
