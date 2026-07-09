import { Injectable, Logger } from '@nestjs/common';
import type { Requirements } from './types';

const SYSTEM_PROMPT = `You extract structured technical requirements from a
free-text description of an AI use case. Reply strictly in the requested JSON
schema. Do not add commentary.`;

const REQUIREMENTS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    requireTools: { type: 'boolean' },
    requireVision: { type: 'boolean' },
    requireJson: { type: 'boolean' },
    minContextWindow: { type: ['integer', 'null'], minimum: 0 },
    qualityTier: { type: 'string', enum: ['basic', 'balanced', 'premium'] },
    modality: {
      type: 'string',
      enum: ['text', 'embedding', 'image', 'audio'],
    },
  },
  required: [
    'requireTools',
    'requireVision',
    'requireJson',
    'minContextWindow',
    'qualityTier',
    'modality',
  ],
} as const;

/**
 * Extracts requirements from a free-text use case. Two paths:
 *  - LLM with json_schema response_format when OPTIMIZER_LLM_API_KEY is set
 *  - Deterministic keyword heuristic otherwise (also used as tests baseline)
 *
 * The heuristic is exported for direct testing.
 */
@Injectable()
export class RequirementsExtractor {
  private readonly logger = new Logger(RequirementsExtractor.name);

  async extract(
    useCase: string,
  ): Promise<{ requirements: Requirements; source: 'llm' | 'heuristic' }> {
    const apiKey = process.env.OPTIMIZER_LLM_API_KEY;
    if (apiKey) {
      try {
        const requirements = await this.extractWithLLM(useCase, apiKey);
        return { requirements, source: 'llm' };
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        this.logger.warn(
          `LLM extraction failed, falling back to heuristic: ${message}`,
        );
      }
    }
    return {
      requirements: extractHeuristic(useCase),
      source: 'heuristic',
    };
  }

  private async extractWithLLM(
    useCase: string,
    apiKey: string,
  ): Promise<Requirements> {
    const url =
      process.env.OPTIMIZER_LLM_URL ??
      'https://api.openai.com/v1/chat/completions';
    const model = process.env.OPTIMIZER_LLM_MODEL ?? 'gpt-4o-mini';

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        temperature: 0,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: useCase },
        ],
        response_format: {
          type: 'json_schema',
          json_schema: {
            name: 'requirements',
            strict: true,
            schema: REQUIREMENTS_SCHEMA,
          },
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`LLM HTTP ${response.status}: ${await response.text()}`);
    }
    const body = (await response.json()) as {
      choices?: { message?: { content?: string } }[];
    };
    const content = body.choices?.[0]?.message?.content;
    if (!content) throw new Error('LLM response missing content');
    return JSON.parse(content) as Requirements;
  }
}

const TOOL_KEYWORDS = [
  'function call',
  'function-calling',
  'tool use',
  'tools',
  'agent',
  'api call',
];
const VISION_KEYWORDS = [
  'vision',
  'image',
  'picture',
  'ocr',
  'screenshot',
  'photo',
];
const JSON_KEYWORDS = [
  'json',
  'structured output',
  'schema',
  'parse',
  'extract fields',
];
const PREMIUM_KEYWORDS = [
  'complex reasoning',
  'critical',
  'production-grade',
  'legal',
  'medical',
  'finance',
  'accuracy',
  'best quality',
  'frontier',
];
const BASIC_KEYWORDS = [
  'cheap',
  'high volume',
  'batch',
  'summarization',
  'classification',
  'tagging',
  'simple',
];
const EMBEDDING_KEYWORDS = ['embedding', 'similarity', 'vector search', 'rag'];
const AUDIO_KEYWORDS = ['transcribe', 'speech', 'audio', 'stt', 'tts'];
const IMAGE_KEYWORDS = [
  'generate image',
  'image generation',
  'dall-e',
  'create image',
];

const CONTEXT_PATTERNS = [
  /(\d+)\s*[kK]\s*(?:tokens|context)?/,
  /(\d+)\s*(?:thousand|k)/i,
  /(\d[\d,]*)\s*tokens?/,
];

export function extractHeuristic(useCase: string): Requirements {
  const t = useCase.toLowerCase();

  const requireTools = TOOL_KEYWORDS.some((k) => t.includes(k));
  const requireVision = VISION_KEYWORDS.some((k) => t.includes(k));
  const requireJson = JSON_KEYWORDS.some((k) => t.includes(k));

  let modality: Requirements['modality'] = 'text';
  if (EMBEDDING_KEYWORDS.some((k) => t.includes(k))) modality = 'embedding';
  else if (AUDIO_KEYWORDS.some((k) => t.includes(k))) modality = 'audio';
  else if (IMAGE_KEYWORDS.some((k) => t.includes(k))) modality = 'image';

  let qualityTier: Requirements['qualityTier'] = 'balanced';
  if (PREMIUM_KEYWORDS.some((k) => t.includes(k))) qualityTier = 'premium';
  else if (BASIC_KEYWORDS.some((k) => t.includes(k))) qualityTier = 'basic';

  let minContextWindow: number | null = null;
  for (const pattern of CONTEXT_PATTERNS) {
    const m = pattern.exec(useCase);
    if (m) {
      const raw = m[1].replace(/,/g, '');
      const n = Number(raw);
      if (!Number.isNaN(n)) {
        minContextWindow = pattern.source.includes('[kK]') ? n * 1000 : n;
        break;
      }
    }
  }

  return {
    requireTools,
    requireVision,
    requireJson,
    minContextWindow,
    qualityTier,
    modality,
  };
}
