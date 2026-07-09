import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { ThrottlerModule } from '@nestjs/throttler';
import { PrismaModule } from '@hedhog/prisma';
import { PricingModule } from './pricing/pricing.module';
import { OptimizerModule } from './optimizer/optimizer.module';

@Module({
  imports: [
    PrismaModule,
    ThrottlerModule.forRoot([{ ttl: 60000, limit: 10 }]),
    PricingModule,
    OptimizerModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
