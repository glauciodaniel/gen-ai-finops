import { Injectable } from '@nestjs/common';
import { PrismaService } from '@hedhog/prisma';
import { costForCandidate } from './cost.calculator';
import type {
  CandidateModel,
  Recommendation,
  Requirements,
  UsageProfile,
} from './types';

@Injectable()
export class CandidatesRanker {
  constructor(private readonly prisma: PrismaService) {}

  async findCandidates(req: Requirements): Promise<CandidateModel[]> {
    const where = {
      deprecated: false,
      modality: req.modality,
      ...(req.requireTools && { supports_tools: true }),
      ...(req.requireVision && { supports_vision: true }),
      ...(req.requireJson && { supports_json: true }),
      ...(req.minContextWindow && {
        context_window: { gte: req.minContextWindow },
      }),
    };

    const rows = await this.prisma.ai_model.findMany({
      where,
      include: {
        provider: { select: { slug: true, name: true } },
        prices: { orderBy: { effective_from: 'desc' }, take: 1 },
      },
    });

    return rows
      .filter((r: any) => r.prices.length > 0)
      .map((r: any) => this.toCandidate(r));
  }

  async findBySlug(slug: string): Promise<CandidateModel | null> {
    const row = await this.prisma.ai_model.findFirst({
      where: { slug },
      include: {
        provider: { select: { slug: true, name: true } },
        prices: { orderBy: { effective_from: 'desc' }, take: 1 },
      },
    });
    if (!row || row.prices.length === 0) return null;
    return this.toCandidate(row);
  }

  /**
   * Rank candidates by (a) meeting requirements, (b) quality tier alignment,
   * (c) cost. Cost weighting is stronger for 'basic' tier, weaker for 'premium'.
   * Returns candidates sorted best-first.
   */
  rank(
    candidates: CandidateModel[],
    req: Requirements,
    usage: UsageProfile,
  ): Recommendation[] {
    const withCost = candidates.map((c) => ({
      candidate: c,
      monthlyCost: costForCandidate(usage, c),
    }));

    const minCost = Math.min(
      ...withCost.map((x) => x.monthlyCost).filter((v) => v > 0),
      Number.POSITIVE_INFINITY,
    );

    return withCost
      .map(({ candidate, monthlyCost }) => {
        const reasoning: string[] = [];
        let score = 100;

        if (candidate.supportsTools && req.requireTools) {
          score += 50;
          reasoning.push('supports function calling');
        }
        if (candidate.supportsVision && req.requireVision) {
          score += 50;
          reasoning.push('supports vision');
        }
        if (candidate.supportsJson && req.requireJson) {
          score += 30;
          reasoning.push('supports structured JSON output');
        }
        if (
          req.minContextWindow &&
          candidate.contextWindow &&
          candidate.contextWindow >= req.minContextWindow * 2
        ) {
          score += 25;
          reasoning.push(
            `context window ${candidate.contextWindow.toLocaleString()} tokens`,
          );
        }

        const tierScore = this.tierScore(candidate, req.qualityTier);
        score += tierScore.points;
        if (tierScore.reason) reasoning.push(tierScore.reason);

        const costWeight = this.costWeight(req.qualityTier);
        if (monthlyCost > 0 && Number.isFinite(minCost) && minCost > 0) {
          const ratio = minCost / monthlyCost;
          score += costWeight * ratio;
          if (Math.abs(monthlyCost - minCost) < 0.01) {
            reasoning.push('cheapest option for this workload');
          }
        }

        return {
          ...candidate,
          score: Math.round(score * 100) / 100,
          monthlyCost,
          reasoning,
        };
      })
      .sort((a, b) => b.score - a.score);
  }

  private toCandidate(row: any): CandidateModel {
    const price = row.prices[0];
    return {
      id: row.id,
      slug: row.slug,
      displayName: row.display_name,
      providerSlug: row.provider.slug,
      providerName: row.provider.name,
      modality: row.modality,
      contextWindow: row.context_window,
      supportsTools: row.supports_tools,
      supportsVision: row.supports_vision,
      supportsJson: row.supports_json,
      inputPer1M: Number(price.input_per_1m),
      outputPer1M: Number(price.output_per_1m),
      cachedInputPer1M:
        price.cached_input_per_1m === null
          ? null
          : Number(price.cached_input_per_1m),
    };
  }

  private tierScore(
    candidate: CandidateModel,
    tier: Requirements['qualityTier'],
  ): { points: number; reason: string | null } {
    // Rough proxy: high output prices correlate with frontier models.
    const p = candidate.outputPer1M;
    const isPremium = p >= 15;
    const isBalanced = p >= 3 && p < 15;
    const isBasic = p < 3;

    if (tier === 'premium' && isPremium)
      return { points: 40, reason: 'premium-tier model' };
    if (tier === 'balanced' && isBalanced)
      return { points: 40, reason: 'balanced price/quality' };
    if (tier === 'basic' && isBasic)
      return { points: 40, reason: 'low-cost tier' };

    if (tier === 'premium' && isBalanced) return { points: 15, reason: null };
    if (tier === 'balanced' && isBasic)
      return { points: 20, reason: 'cheaper than target tier' };
    if (tier === 'balanced' && isPremium) return { points: 10, reason: null };
    if (tier === 'basic' && isBalanced) return { points: 5, reason: null };

    return { points: 0, reason: null };
  }

  private costWeight(tier: Requirements['qualityTier']): number {
    if (tier === 'basic') return 120;
    if (tier === 'balanced') return 60;
    return 25; // premium: cost matters less
  }
}
