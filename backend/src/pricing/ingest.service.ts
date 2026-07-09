import {
  BadRequestException,
  Injectable,
  Logger,
} from '@nestjs/common';
import { PrismaService } from '@hedhog/prisma';
import { IngestBatchDto, IngestModelDto, IngestResult } from './dto/ingest.dto';

const MIN_MODELS_PER_PROVIDER = 3;
const PRICE_EPSILON = 0.000001;

@Injectable()
export class IngestService {
  private readonly logger = new Logger(IngestService.name);

  constructor(private readonly prisma: PrismaService) {}

  async ingest(batch: IngestBatchDto): Promise<IngestResult> {
    const errors: string[] = [];

    if (batch.models.length < MIN_MODELS_PER_PROVIDER) {
      throw new BadRequestException(
        `Batch contains ${batch.models.length} models, minimum is ${MIN_MODELS_PER_PROVIDER}`,
      );
    }

    const provider = await this.prisma.provider.findUnique({
      where: { slug: batch.provider },
    });
    if (!provider) {
      throw new BadRequestException(`Unknown provider: ${batch.provider}`);
    }

    const scrapeRun = await this.prisma.scrape_run.create({
      data: {
        status: 'running',
        provider: batch.provider,
        items_found: batch.models.length,
      },
    });

    let itemsChanged = 0;

    try {
      for (const model of batch.models) {
        try {
          const changed = await this.upsertModelAndPrice(
            provider.id,
            model,
            batch.source,
            scrapeRun.id,
          );
          if (changed) itemsChanged++;
        } catch (err) {
          const message = err instanceof Error ? err.message : String(err);
          errors.push(`${model.slug}: ${message}`);
          this.logger.warn(
            `Failed to ingest model ${model.slug}: ${message}`,
          );
        }
      }

      const status: IngestResult['status'] =
        errors.length === 0
          ? 'success'
          : errors.length < batch.models.length
            ? 'partial'
            : 'failed';

      await this.prisma.scrape_run.update({
        where: { id: scrapeRun.id },
        data: {
          finished_at: new Date(),
          status,
          items_changed: itemsChanged,
          error_log: errors.length ? errors.join('\n') : null,
        },
      });

      return {
        scrapeRunId: scrapeRun.id,
        status,
        itemsFound: batch.models.length,
        itemsChanged,
        errors,
      };
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      await this.prisma.scrape_run.update({
        where: { id: scrapeRun.id },
        data: {
          finished_at: new Date(),
          status: 'failed',
          error_log: message,
        },
      });
      throw err;
    }
  }

  private async upsertModelAndPrice(
    providerId: number,
    model: IngestModelDto,
    source: string,
    scrapeRunId: number,
  ): Promise<boolean> {
    const aiModel = await this.prisma.ai_model.upsert({
      where: {
        provider_id_slug: { provider_id: providerId, slug: model.slug },
      },
      create: {
        provider_id: providerId,
        slug: model.slug,
        display_name: model.displayName,
        modality: model.modality ?? 'text',
        context_window: model.contextWindow ?? null,
        max_output: model.maxOutput ?? null,
        supports_tools: model.supportsTools ?? false,
        supports_vision: model.supportsVision ?? false,
        supports_json: model.supportsJson ?? false,
        deprecated: model.deprecated ?? false,
      },
      update: {
        display_name: model.displayName,
        modality: model.modality ?? 'text',
        context_window: model.contextWindow ?? null,
        max_output: model.maxOutput ?? null,
        supports_tools: model.supportsTools ?? false,
        supports_vision: model.supportsVision ?? false,
        supports_json: model.supportsJson ?? false,
        deprecated: model.deprecated ?? false,
      },
    });

    const lastPrice = await this.prisma.model_price.findFirst({
      where: { model_id: aiModel.id },
      orderBy: { effective_from: 'desc' },
    });

    const priceChanged =
      !lastPrice ||
      !this.decimalEquals(lastPrice.input_per_1m, model.inputPer1M) ||
      !this.decimalEquals(lastPrice.output_per_1m, model.outputPer1M) ||
      !this.decimalEquals(
        lastPrice.cached_input_per_1m,
        model.cachedInputPer1M ?? null,
      );

    if (!priceChanged) return false;

    await this.prisma.model_price.create({
      data: {
        model_id: aiModel.id,
        input_per_1m: model.inputPer1M,
        output_per_1m: model.outputPer1M,
        cached_input_per_1m: model.cachedInputPer1M ?? null,
        currency: model.currency ?? 'USD',
        source,
        scrape_run_id: scrapeRunId,
      },
    });
    return true;
  }

  private decimalEquals(a: unknown, b: number | null): boolean {
    if (a === null && b === null) return true;
    if (a === null || b === null) return false;
    return Math.abs(Number(a) - b) < PRICE_EPSILON;
  }
}
