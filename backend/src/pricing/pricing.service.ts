import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '@hedhog/prisma';

@Injectable()
export class PricingService {
  constructor(private readonly prisma: PrismaService) {}

  async getProviders() {
    return this.prisma.provider.findMany({ orderBy: { slug: 'asc' } });
  }

  async getModels(params: {
    provider?: string;
    modality?: string;
    page?: number;
    limit?: number;
  }) {
    const { provider, modality, page = 1, limit = 20 } = params;
    const skip = (page - 1) * limit;

    const where = {
      deprecated: false,
      ...(modality && { modality }),
      ...(provider && { provider: { slug: provider } }),
    };

    const [items, total] = await Promise.all([
      this.prisma.ai_model.findMany({
        where,
        include: {
          provider: { select: { slug: true, name: true } },
          model_price: {
            orderBy: { effective_from: 'desc' },
            take: 1,
          },
        },
        skip,
        take: limit,
        orderBy: [{ provider: { slug: 'asc' } }, { slug: 'asc' }],
      }),
      this.prisma.ai_model.count({ where }),
    ]);

    return { items, total, page, limit, pages: Math.ceil(total / limit) };
  }

  async getModelHistory(slug: string, days: number) {
    const model = await this.prisma.ai_model.findFirst({
      where: { slug },
      include: { provider: { select: { slug: true, name: true } } },
    });
    if (!model) throw new NotFoundException(`Model ${slug} not found`);

    const since = new Date();
    since.setDate(since.getDate() - days);

    const prices = await this.prisma.model_price.findMany({
      where: { model_id: model.id, effective_from: { gte: since } },
      orderBy: { effective_from: 'asc' },
    });

    return { model, prices };
  }

  async getScrapeRuns(limit = 20) {
    return this.prisma.scrape_run.findMany({
      orderBy: { started_at: 'desc' },
      take: limit,
    });
  }

  async compareModels(slugs: string[]) {
    if (!slugs.length) return { items: [] };

    const models = await this.prisma.ai_model.findMany({
      where: { slug: { in: slugs } },
      include: {
        provider: { select: { slug: true, name: true } },
        model_price: { orderBy: { effective_from: 'desc' }, take: 1 },
      },
    });

    const found = new Set(models.map((m) => m.slug));
    const missing = slugs.filter((s) => !found.has(s));

    return { items: models, missing };
  }

  async getStats() {
    const [providers, activeModels, totalPrices, lastRun] = await Promise.all([
      this.prisma.provider.count(),
      this.prisma.ai_model.count({ where: { deprecated: false } }),
      this.prisma.model_price.count(),
      this.prisma.scrape_run.findFirst({
        where: { status: { in: ['success', 'partial'] } },
        orderBy: { finished_at: 'desc' },
      }),
    ]);

    return {
      providers,
      activeModels,
      priceRecords: totalPrices,
      lastScrapeAt: lastRun?.finished_at ?? null,
      lastScrapeStatus: lastRun?.status ?? null,
    };
  }
}
