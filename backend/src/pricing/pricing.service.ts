import { Injectable } from '@nestjs/common';
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
}
