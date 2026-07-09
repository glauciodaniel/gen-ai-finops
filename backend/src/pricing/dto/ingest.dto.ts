import {
  IsArray,
  IsBoolean,
  IsIn,
  IsInt,
  IsNumber,
  IsOptional,
  IsString,
  Length,
  Min,
  ValidateNested,
} from 'class-validator';
import { Type } from 'class-transformer';

export class IngestModelDto {
  @IsString()
  @Length(1, 100)
  slug!: string;

  @IsString()
  @Length(1, 150)
  displayName!: string;

  @IsOptional()
  @IsIn(['text', 'embedding', 'image', 'audio'])
  modality?: string;

  @IsOptional()
  @IsInt()
  @Min(1)
  contextWindow?: number;

  @IsOptional()
  @IsInt()
  @Min(1)
  maxOutput?: number;

  @IsOptional()
  @IsBoolean()
  supportsTools?: boolean;

  @IsOptional()
  @IsBoolean()
  supportsVision?: boolean;

  @IsOptional()
  @IsBoolean()
  supportsJson?: boolean;

  @IsOptional()
  @IsBoolean()
  deprecated?: boolean;

  @IsNumber({ maxDecimalPlaces: 6 })
  @Min(0)
  inputPer1M!: number;

  @IsNumber({ maxDecimalPlaces: 6 })
  @Min(0)
  outputPer1M!: number;

  @IsOptional()
  @IsNumber({ maxDecimalPlaces: 6 })
  @Min(0)
  cachedInputPer1M?: number;

  @IsOptional()
  @IsString()
  @Length(3, 3)
  currency?: string;
}

export class IngestBatchDto {
  @IsString()
  @Length(1, 50)
  provider!: string;

  @IsString()
  @Length(1, 500)
  source!: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => IngestModelDto)
  models!: IngestModelDto[];
}

export interface IngestResult {
  scrapeRunId: number;
  status: 'success' | 'partial' | 'failed';
  itemsFound: number;
  itemsChanged: number;
  errors: string[];
}
