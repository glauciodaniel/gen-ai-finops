import { MigrationInterface, QueryRunner } from 'typeorm';

export class CreatePricingTables1720526400000 implements MigrationInterface {
  name = 'CreatePricingTables1720526400000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      CREATE TABLE "provider" (
        "id" SERIAL PRIMARY KEY,
        "slug" VARCHAR(50) NOT NULL UNIQUE,
        "name" VARCHAR(100) NOT NULL,
        "pricing_url" VARCHAR(500)
      )
    `);

    await queryRunner.query(`
      CREATE TABLE "ai_model" (
        "id" SERIAL PRIMARY KEY,
        "provider_id" INTEGER NOT NULL REFERENCES "provider"("id"),
        "slug" VARCHAR(100) NOT NULL,
        "display_name" VARCHAR(150) NOT NULL,
        "modality" VARCHAR(20) NOT NULL DEFAULT 'text',
        "context_window" INTEGER,
        "max_output" INTEGER,
        "supports_tools" BOOLEAN NOT NULL DEFAULT false,
        "supports_vision" BOOLEAN NOT NULL DEFAULT false,
        "supports_json" BOOLEAN NOT NULL DEFAULT false,
        "deprecated" BOOLEAN NOT NULL DEFAULT false,
        CONSTRAINT "uq_ai_model_provider_slug" UNIQUE ("provider_id", "slug")
      )
    `);

    await queryRunner.query(`
      CREATE TABLE "scrape_run" (
        "id" SERIAL PRIMARY KEY,
        "started_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
        "finished_at" TIMESTAMPTZ,
        "status" VARCHAR(20) NOT NULL DEFAULT 'running',
        "provider" VARCHAR(50),
        "items_found" INTEGER NOT NULL DEFAULT 0,
        "items_changed" INTEGER NOT NULL DEFAULT 0,
        "error_log" TEXT
      )
    `);

    await queryRunner.query(`
      CREATE TABLE "model_price" (
        "id" SERIAL PRIMARY KEY,
        "model_id" INTEGER NOT NULL REFERENCES "ai_model"("id"),
        "input_per_1m" DECIMAL(12,6) NOT NULL,
        "output_per_1m" DECIMAL(12,6) NOT NULL,
        "cached_input_per_1m" DECIMAL(12,6),
        "currency" VARCHAR(3) NOT NULL DEFAULT 'USD',
        "effective_from" TIMESTAMPTZ NOT NULL DEFAULT now(),
        "source" VARCHAR(500) NOT NULL,
        "scrape_run_id" INTEGER REFERENCES "scrape_run"("id")
      )
    `);

    await queryRunner.query(
      `CREATE INDEX "idx_model_price_model_effective" ON "model_price" ("model_id", "effective_from" DESC)`,
    );

    // Seed the three initial providers
    await queryRunner.query(`
      INSERT INTO "provider" ("slug", "name", "pricing_url") VALUES
        ('openai', 'OpenAI', 'https://platform.openai.com/docs/pricing'),
        ('anthropic', 'Anthropic', 'https://www.anthropic.com/pricing'),
        ('google', 'Google DeepMind', 'https://ai.google.dev/pricing')
    `);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`DROP INDEX IF EXISTS "idx_model_price_model_effective"`);
    await queryRunner.query(`DROP TABLE IF EXISTS "model_price"`);
    await queryRunner.query(`DROP TABLE IF EXISTS "scrape_run"`);
    await queryRunner.query(`DROP TABLE IF EXISTS "ai_model"`);
    await queryRunner.query(`DROP TABLE IF EXISTS "provider"`);
  }
}
