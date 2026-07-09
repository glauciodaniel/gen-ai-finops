import {
  Body,
  Controller,
  Get,
  Param,
  Post,
  Query,
  UseGuards,
} from '@nestjs/common';
import { PricingService } from './pricing.service';
import { IngestService } from './ingest.service';
import { IngestBatchDto, IngestResult } from './dto/ingest.dto';
import { ServiceTokenGuard } from './guards/service-token.guard';

@Controller('pricing')
export class PricingController {
  constructor(
    private readonly pricingService: PricingService,
    private readonly ingestService: IngestService,
  ) {}

  @Get('providers')
  getProviders() {
    return this.pricingService.getProviders();
  }

  @Get('models')
  getModels(
    @Query('provider') provider?: string,
    @Query('modality') modality?: string,
    @Query('page') page?: string,
    @Query('limit') limit?: string,
  ) {
    return this.pricingService.getModels({
      provider,
      modality,
      page: page ? parseInt(page, 10) : 1,
      limit: limit ? parseInt(limit, 10) : 20,
    });
  }

  @Get('models/:slug/history')
  getModelHistory(
    @Param('slug') slug: string,
    @Query('days') days?: string,
  ) {
    return this.pricingService.getModelHistory(
      slug,
      days ? parseInt(days, 10) : 30,
    );
  }

  @Get('scrape-runs')
  getScrapeRuns(@Query('limit') limit?: string) {
    return this.pricingService.getScrapeRuns(
      limit ? parseInt(limit, 10) : 20,
    );
  }

  @Get('compare')
  compareModels(@Query('models') models?: string) {
    const slugs = (models ?? '')
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    return this.pricingService.compareModels(slugs);
  }

  @Get('stats')
  getStats() {
    return this.pricingService.getStats();
  }

  @Post('ingest')
  @UseGuards(ServiceTokenGuard)
  ingest(@Body() batch: IngestBatchDto): Promise<IngestResult> {
    return this.ingestService.ingest(batch);
  }
}
