import {
  IsBoolean,
  IsIn,
  IsInt,
  IsNumber,
  IsOptional,
  IsString,
  Length,
  Min,
} from 'class-validator';

export class OptimizeRequestDto {
  @IsString()
  @Length(1, 2000)
  useCase!: string;

  @IsOptional()
  @IsInt()
  @Min(1)
  inputTokensPerRequest?: number;

  @IsOptional()
  @IsInt()
  @Min(1)
  outputTokensPerRequest?: number;

  @IsOptional()
  @IsInt()
  @Min(1)
  monthlyRequests?: number;

  @IsOptional()
  @IsBoolean()
  requireTools?: boolean;

  @IsOptional()
  @IsBoolean()
  requireVision?: boolean;

  @IsOptional()
  @IsBoolean()
  requireJson?: boolean;

  @IsOptional()
  @IsInt()
  @Min(1)
  minContextWindow?: number;

  @IsOptional()
  @IsIn(['basic', 'balanced', 'premium'])
  qualityTier?: 'basic' | 'balanced' | 'premium';

  @IsOptional()
  @IsIn(['text', 'embedding', 'image', 'audio'])
  modality?: 'text' | 'embedding' | 'image' | 'audio';

  @IsOptional()
  @IsString()
  currentModelSlug?: string;

  @IsOptional()
  @IsInt()
  @Min(1)
  topN?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  maxMonthlyBudget?: number;
}
