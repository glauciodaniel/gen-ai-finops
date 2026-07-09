import { Body, Controller, Post } from '@nestjs/common';
import { OptimizeRequestDto } from './dto/optimize.dto';
import { OptimizerService } from './optimizer.service';

@Controller('optimizer')
export class OptimizerController {
  constructor(private readonly optimizer: OptimizerService) {}

  @Post('analyze')
  analyze(@Body() body: OptimizeRequestDto) {
    return this.optimizer.optimize(body);
  }
}
