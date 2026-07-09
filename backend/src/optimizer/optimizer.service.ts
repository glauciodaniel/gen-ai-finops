import { BadRequestException, Injectable } from '@nestjs/common';
import { CandidatesRanker } from './candidates.ranker';
import { projectSavings } from './cost.calculator';
import { OptimizeRequestDto } from './dto/optimize.dto';
import { RequirementsExtractor } from './requirements.extractor';
import type { OptimizeResult, Requirements, UsageProfile } from './types';

const DEFAULT_INPUT_TOKENS = 500;
const DEFAULT_OUTPUT_TOKENS = 500;
const DEFAULT_MONTHLY_REQUESTS = 100_000;
const DEFAULT_TOP_N = 5;

@Injectable()
export class OptimizerService {
  constructor(
    private readonly extractor: RequirementsExtractor,
    private readonly ranker: CandidatesRanker,
  ) {}

  async optimize(req: OptimizeRequestDto): Promise<OptimizeResult> {
    const usage = this.usageFrom(req);
    const { requirements, source } = await this.buildRequirements(req);

    const candidates = await this.ranker.findCandidates(requirements);
    if (!candidates.length) {
      throw new BadRequestException(
        'No models match the given requirements. Try relaxing the filters.',
      );
    }

    let ranked = this.ranker.rank(candidates, requirements, usage);

    if (req.maxMonthlyBudget !== undefined) {
      const withinBudget = ranked.filter(
        (r) => r.monthlyCost <= req.maxMonthlyBudget!,
      );
      if (withinBudget.length > 0) ranked = withinBudget;
    }

    const topN = req.topN ?? DEFAULT_TOP_N;
    const recommendations = ranked.slice(0, topN);

    let savings: OptimizeResult['savings'] = null;
    if (req.currentModelSlug && recommendations.length > 0) {
      const current = await this.ranker.findBySlug(req.currentModelSlug);
      if (current) {
        savings = projectSavings(usage, current, recommendations[0]);
      }
    }

    return {
      requirements,
      usage,
      recommendations,
      savings,
      requirementsSource: source,
    };
  }

  private usageFrom(req: OptimizeRequestDto): UsageProfile {
    return {
      inputTokensPerRequest:
        req.inputTokensPerRequest ?? DEFAULT_INPUT_TOKENS,
      outputTokensPerRequest:
        req.outputTokensPerRequest ?? DEFAULT_OUTPUT_TOKENS,
      monthlyRequests: req.monthlyRequests ?? DEFAULT_MONTHLY_REQUESTS,
    };
  }

  private async buildRequirements(
    req: OptimizeRequestDto,
  ): Promise<{ requirements: Requirements; source: 'user' | 'llm' | 'heuristic' }> {
    const userOverrides = this.userProvidedRequirements(req);
    const anyOverride = Object.values(userOverrides).some((v) => v !== undefined);

    const base =
      anyOverride && req.useCase.trim().length === 0
        ? { requirements: this.defaultRequirements(), source: 'user' as const }
        : { ...(await this.extractor.extract(req.useCase)) };

    return {
      requirements: { ...base.requirements, ...compact(userOverrides) },
      source: anyOverride ? 'user' : base.source,
    };
  }

  private userProvidedRequirements(
    req: OptimizeRequestDto,
  ): Partial<Requirements> {
    return {
      requireTools: req.requireTools,
      requireVision: req.requireVision,
      requireJson: req.requireJson,
      minContextWindow: req.minContextWindow,
      qualityTier: req.qualityTier,
      modality: req.modality,
    };
  }

  private defaultRequirements(): Requirements {
    return {
      requireTools: false,
      requireVision: false,
      requireJson: false,
      minContextWindow: null,
      qualityTier: 'balanced',
      modality: 'text',
    };
  }
}

function compact<T extends object>(obj: T): Partial<T> {
  const out: Partial<T> = {};
  for (const [k, v] of Object.entries(obj)) {
    if (v !== undefined) (out as any)[k] = v;
  }
  return out;
}
