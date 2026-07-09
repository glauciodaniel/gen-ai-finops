import {
  CanActivate,
  ExecutionContext,
  Injectable,
  Logger,
  UnauthorizedException,
} from '@nestjs/common';
import { Request } from 'express';

@Injectable()
export class ServiceTokenGuard implements CanActivate {
  private readonly logger = new Logger(ServiceTokenGuard.name);

  canActivate(context: ExecutionContext): boolean {
    const expected = process.env.PRICING_INGEST_TOKEN;
    if (!expected) {
      this.logger.error(
        'PRICING_INGEST_TOKEN not configured; rejecting ingest request',
      );
      throw new UnauthorizedException('Ingest not configured');
    }

    const req = context.switchToHttp().getRequest<Request>();
    const header = req.headers['authorization'] ?? '';
    const match = /^Bearer\s+(.+)$/i.exec(header);
    const token = match?.[1];

    if (!token || token !== expected) {
      throw new UnauthorizedException('Invalid ingest token');
    }
    return true;
  }
}
