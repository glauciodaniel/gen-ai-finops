import { CandidatesRanker } from './candidates.ranker';
import type { CandidateModel, Requirements, UsageProfile } from './types';

function candidate(overrides: Partial<CandidateModel> = {}): CandidateModel {
  return {
    id: 1,
    slug: 'model',
    displayName: 'Model',
    providerSlug: 'openai',
    providerName: 'OpenAI',
    modality: 'text',
    contextWindow: 128000,
    supportsTools: false,
    supportsVision: false,
    supportsJson: false,
    inputPer1M: 5,
    outputPer1M: 5,
    cachedInputPer1M: null,
    ...overrides,
  };
}

function reqs(overrides: Partial<Requirements> = {}): Requirements {
  return {
    requireTools: false,
    requireVision: false,
    requireJson: false,
    minContextWindow: null,
    qualityTier: 'balanced',
    modality: 'text',
    ...overrides,
  };
}

const usage: UsageProfile = {
  inputTokensPerRequest: 1_000,
  outputTokensPerRequest: 500,
  monthlyRequests: 100_000,
};

describe('CandidatesRanker.rank', () => {
  // PrismaService is not needed for rank() tests — the ranker is instantiated
  // with a null-cast so we don't pull the entire Prisma client into the suite.
  const ranker = new CandidatesRanker(null as never);

  it('sorts by score descending', () => {
    const results = ranker.rank(
      [
        candidate({ slug: 'a', outputPer1M: 5 }),
        candidate({ slug: 'b', outputPer1M: 0.5 }),
        candidate({ slug: 'c', outputPer1M: 20 }),
      ],
      reqs(),
      usage,
    );
    for (let i = 1; i < results.length; i++) {
      expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
    }
  });

  it('rewards models that satisfy a required capability', () => {
    const [withTools, withoutTools] = ranker.rank(
      [
        candidate({ slug: 'with-tools', supportsTools: true, outputPer1M: 5 }),
        candidate({ slug: 'no-tools', supportsTools: false, outputPer1M: 5 }),
      ],
      reqs({ requireTools: true }),
      usage,
    );
    expect(withTools.slug).toBe('with-tools');
    expect(withTools.reasoning).toContain('supports function calling');
    expect(withTools.score).toBeGreaterThan(withoutTools.score);
  });

  it('for basic tier, cheapest option wins when capabilities are equal', () => {
    const results = ranker.rank(
      [
        candidate({ slug: 'expensive', inputPer1M: 30, outputPer1M: 60 }),
        candidate({ slug: 'cheap', inputPer1M: 0.15, outputPer1M: 0.6 }),
      ],
      reqs({ qualityTier: 'basic' }),
      usage,
    );
    expect(results[0].slug).toBe('cheap');
    expect(results[0].reasoning).toContain('cheapest option for this workload');
  });

  it('for premium tier, expensive high-quality wins over cheap basic', () => {
    const results = ranker.rank(
      [
        candidate({ slug: 'basic', outputPer1M: 0.6 }),
        candidate({ slug: 'premium', outputPer1M: 60 }),
      ],
      reqs({ qualityTier: 'premium' }),
      usage,
    );
    expect(results[0].slug).toBe('premium');
    expect(results[0].reasoning).toContain('premium-tier model');
  });

  it('rewards a large context window when requirements set a minimum', () => {
    const results = ranker.rank(
      [
        candidate({ slug: 'small', contextWindow: 32_000 }),
        candidate({ slug: 'huge', contextWindow: 1_000_000 }),
      ],
      reqs({ minContextWindow: 100_000 }),
      usage,
    );
    const huge = results.find((r) => r.slug === 'huge')!;
    expect(huge.reasoning.some((r) => r.includes('context window'))).toBe(true);
  });

  it('attaches a monthly cost to each recommendation', () => {
    const results = ranker.rank(
      [candidate({ slug: 'x', inputPer1M: 2.5, outputPer1M: 10 })],
      reqs(),
      usage,
    );
    expect(results[0].monthlyCost).toBe(750);
  });
});
