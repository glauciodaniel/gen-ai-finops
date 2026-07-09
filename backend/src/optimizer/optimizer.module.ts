import { Module } from '@nestjs/common';
import { OptimizerController } from './optimizer.controller';
import { OptimizerService } from './optimizer.service';
import { CandidatesRanker } from './candidates.ranker';
import { RequirementsExtractor } from './requirements.extractor';

@Module({
  controllers: [OptimizerController],
  providers: [OptimizerService, CandidatesRanker, RequirementsExtractor],
  exports: [OptimizerService],
})
export class OptimizerModule {}
