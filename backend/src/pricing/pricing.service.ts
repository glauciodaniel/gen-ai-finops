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
          prices: {
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
}
