import { Controller, Get, Query } from '@nestjs/common';
import { PricingService } from './pricing.service';

@Controller('pricing')
export class PricingController {
  constructor(private readonly pricingService: PricingService) {}

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
      page: page ? parseInt(page) : 1,
      limit: limit ? parseInt(limit) : 20,
    });
  }
}
