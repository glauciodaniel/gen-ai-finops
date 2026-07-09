import { Module } from '@nestjs/common';
import { PricingController } from './pricing.controller';
import { PricingService } from './pricing.service';
import { IngestService } from './ingest.service';

@Module({
  controllers: [PricingController],
  providers: [PricingService, IngestService],
  exports: [PricingService, IngestService],
})
export class PricingModule {}
