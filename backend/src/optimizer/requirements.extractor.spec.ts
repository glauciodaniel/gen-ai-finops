import { extractHeuristic } from './requirements.extractor';

describe('extractHeuristic', () => {
  it('detects function-calling keywords', () => {
    expect(extractHeuristic('agent that uses function calling').requireTools).toBe(true);
    expect(extractHeuristic('simple chatbot').requireTools).toBe(false);
  });

  it('detects vision keywords', () => {
    expect(extractHeuristic('OCR pipeline for screenshots').requireVision).toBe(true);
    expect(extractHeuristic('text summarization').requireVision).toBe(false);
  });

  it('detects JSON output keywords', () => {
    expect(extractHeuristic('extract fields as JSON with schema').requireJson).toBe(true);
    expect(extractHeuristic('friendly reply').requireJson).toBe(false);
  });

  it('sets qualityTier to premium for high-stakes language', () => {
    expect(
      extractHeuristic('critical legal review with complex reasoning').qualityTier,
    ).toBe('premium');
  });

  it('sets qualityTier to basic for high-volume simple tasks', () => {
    expect(
      extractHeuristic('cheap tagging for a high volume of tickets').qualityTier,
    ).toBe('basic');
  });

  it('defaults qualityTier to balanced when nothing matches', () => {
    expect(extractHeuristic('customer support bot').qualityTier).toBe('balanced');
  });

  it('picks up embedding modality', () => {
    expect(extractHeuristic('build a RAG with vector search').modality).toBe('embedding');
  });

  it('extracts a context window hint expressed in k', () => {
    expect(
      extractHeuristic('long doc analysis, need 128k context').minContextWindow,
    ).toBe(128_000);
  });

  it('extracts a context window hint expressed as "N thousand"', () => {
    // Regression: prior implementation matched the pattern but returned N
    // instead of N * 1000 for the "thousand" phrasing.
    expect(
      extractHeuristic('want at least 128 thousand tokens of context')
        .minContextWindow,
    ).toBe(128_000);
  });

  it('extracts a raw token count with commas', () => {
    expect(
      extractHeuristic('needs 200,000 tokens of context').minContextWindow,
    ).toBe(200_000);
  });

  it('returns null when no context hint is present', () => {
    expect(extractHeuristic('just a friendly chatbot').minContextWindow).toBeNull();
  });
});
