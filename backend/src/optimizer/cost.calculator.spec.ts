import {
  calculateMonthlyCost,
  costForCandidate,
  projectSavings,
} from './cost.calculator';
import type { CandidateModel, UsageProfile } from './types';

function candidate(overrides: Partial<CandidateModel> = {}): CandidateModel {
  return {
    id: 1,
    slug: 'gpt-4o',
    displayName: 'GPT-4o',
    providerSlug: 'openai',
    providerName: 'OpenAI',
    modality: 'text',
    contextWindow: 128000,
    supportsTools: true,
    supportsVision: true,
    supportsJson: true,
    inputPer1M: 2.5,
    outputPer1M: 10,
    cachedInputPer1M: 1.25,
    ...overrides,
  };
}

describe('calculateMonthlyCost', () => {
  const usage: UsageProfile = {
    inputTokensPerRequest: 1_000,
    outputTokensPerRequest: 500,
    monthlyRequests: 100_000,
  };

  it('computes cost as sum of input+output prices scaled to monthly volume', () => {
    // per-request: (1000/1M * $2.5) + (500/1M * $10) = 0.0025 + 0.005 = 0.0075
    // monthly: 0.0075 * 100000 = $750
    expect(calculateMonthlyCost(usage, 2.5, 10)).toBe(750);
  });

  it('returns 0 when the model is free (both prices zero)', () => {
    expect(calculateMonthlyCost(usage, 0, 0)).toBe(0);
  });

  it('scales linearly with request volume', () => {
    const a = calculateMonthlyCost(usage, 2.5, 10);
    const b = calculateMonthlyCost({ ...usage, monthlyRequests: 200_000 }, 2.5, 10);
    expect(b).toBe(a * 2);
  });

  it('rounds to 2 decimals', () => {
    const cost = calculateMonthlyCost(
      { inputTokensPerRequest: 1, outputTokensPerRequest: 1, monthlyRequests: 1 },
      1.23456,
      1.23456,
    );
    // Both partial per-token costs are tiny; verify no float noise leaks.
    expect(cost).toBe(0);
  });
});

describe('costForCandidate', () => {
  it('delegates to calculateMonthlyCost with candidate prices', () => {
    const usage: UsageProfile = {
      inputTokensPerRequest: 2_000,
      outputTokensPerRequest: 1_000,
      monthlyRequests: 50_000,
    };
    // per-request: (2000/1M * 2.5) + (1000/1M * 10) = 0.005 + 0.01 = 0.015
    // monthly: 0.015 * 50000 = 750
    expect(costForCandidate(usage, candidate())).toBe(750);
  });
});

describe('projectSavings', () => {
  const usage: UsageProfile = {
    inputTokensPerRequest: 1_000,
    outputTokensPerRequest: 500,
    monthlyRequests: 100_000,
  };

  it('reports positive savings when recommended is cheaper than current', () => {
    const current = candidate({ slug: 'gpt-4', inputPer1M: 30, outputPer1M: 60 });
    const recommended = candidate({ slug: 'gpt-4o-mini', inputPer1M: 0.15, outputPer1M: 0.6 });
    const s = projectSavings(usage, current, recommended);

    // current: (1000/1M * 30) + (500/1M * 60) = 0.03 + 0.03 = 0.06 * 100_000 = 6000
    // rec:     (1000/1M * 0.15) + (500/1M * 0.6) = 0.00015 + 0.0003 = 0.00045 * 100_000 = 45
    expect(s.currentMonthlyCost).toBe(6000);
    expect(s.recommendedMonthlyCost).toBe(45);
    expect(s.monthlySavings).toBe(5955);
    expect(s.annualSavings).toBe(5955 * 12);
    expect(s.savingsPercent).toBeGreaterThan(99);
  });

  it('reports negative savings when recommended is more expensive', () => {
    const current = candidate({ inputPer1M: 0.15, outputPer1M: 0.6 });
    const recommended = candidate({ inputPer1M: 30, outputPer1M: 60 });
    const s = projectSavings(usage, current, recommended);
    expect(s.monthlySavings).toBeLessThan(0);
    expect(s.savingsPercent).toBeLessThan(0);
  });

  it('returns 0 percent savings if current cost is zero', () => {
    const current = candidate({ inputPer1M: 0, outputPer1M: 0 });
    const recommended = candidate();
    const s = projectSavings(usage, current, recommended);
    expect(s.savingsPercent).toBe(0);
  });
});
