import { PageTitle } from '@/components/custom/page-title'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useOptimizerAnalyze } from '@/features/optimizer/api'
import type {
  OptimizerRecommendation,
  OptimizerRequest,
} from '@/features/pricing/types'
import { useState } from 'react'

function formatUSD(n: number): string {
  return `$${n.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function RecommendationCard({
  item,
  isTop,
}: {
  item: OptimizerRecommendation
  isTop: boolean
}) {
  return (
    <Card className={isTop ? 'border-primary' : undefined}>
      <CardHeader>
        <div className='flex items-center justify-between'>
          <CardTitle className='text-lg'>{item.displayName}</CardTitle>
          {isTop && <Badge>top pick</Badge>}
        </div>
        <CardDescription>
          {item.providerName} · <code>{item.slug}</code>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className='grid grid-cols-3 gap-4 text-sm'>
          <div>
            <div className='text-xs text-muted-foreground'>Monthly cost</div>
            <div className='text-lg font-bold'>{formatUSD(item.monthlyCost)}</div>
          </div>
          <div>
            <div className='text-xs text-muted-foreground'>Input / 1M</div>
            <div>${item.inputPer1M.toFixed(item.inputPer1M < 1 ? 4 : 2)}</div>
          </div>
          <div>
            <div className='text-xs text-muted-foreground'>Output / 1M</div>
            <div>${item.outputPer1M.toFixed(item.outputPer1M < 1 ? 4 : 2)}</div>
          </div>
        </div>
        {item.reasoning.length > 0 && (
          <ul className='mt-3 list-disc pl-5 text-sm text-muted-foreground'>
            {item.reasoning.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}

export default function Page() {
  const [useCase, setUseCase] = useState('')
  const [inputTokens, setInputTokens] = useState('500')
  const [outputTokens, setOutputTokens] = useState('500')
  const [monthlyRequests, setMonthlyRequests] = useState('100000')
  const [currentSlug, setCurrentSlug] = useState('')

  const analyze = useOptimizerAnalyze()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload: OptimizerRequest = {
      useCase,
      inputTokensPerRequest: Number(inputTokens) || undefined,
      outputTokensPerRequest: Number(outputTokens) || undefined,
      monthlyRequests: Number(monthlyRequests) || undefined,
      currentModelSlug: currentSlug || undefined,
    }
    analyze.mutate(payload)
  }

  const result = analyze.data

  return (
    <>
      <PageTitle title='Cost Optimizer' />

      <p className='my-4 text-sm text-muted-foreground'>
        Describe your use case and expected volume. The optimizer extracts
        requirements, ranks candidate models against live prices, and estimates
        savings if you give it your current model.
      </p>

      <form onSubmit={handleSubmit} className='mb-6 space-y-4'>
        <div>
          <label className='mb-1 block text-sm font-medium'>Use case</label>
          <Textarea
            value={useCase}
            onChange={(e) => setUseCase(e.target.value)}
            placeholder='e.g., Customer support chatbot with function calling for order lookup; ~500 tokens in, ~500 tokens out, ~100k messages/month'
            rows={4}
            required
          />
        </div>
        <div className='grid gap-4 sm:grid-cols-2 md:grid-cols-4'>
          <div>
            <label className='mb-1 block text-sm font-medium'>Input tokens / request</label>
            <Input type='number' min={1} value={inputTokens} onChange={(e) => setInputTokens(e.target.value)} />
          </div>
          <div>
            <label className='mb-1 block text-sm font-medium'>Output tokens / request</label>
            <Input type='number' min={1} value={outputTokens} onChange={(e) => setOutputTokens(e.target.value)} />
          </div>
          <div>
            <label className='mb-1 block text-sm font-medium'>Monthly requests</label>
            <Input type='number' min={1} value={monthlyRequests} onChange={(e) => setMonthlyRequests(e.target.value)} />
          </div>
          <div>
            <label className='mb-1 block text-sm font-medium'>Current model (optional)</label>
            <Input placeholder='e.g., gpt-4' value={currentSlug} onChange={(e) => setCurrentSlug(e.target.value)} />
          </div>
        </div>
        <Button type='submit' disabled={analyze.isPending}>
          {analyze.isPending ? 'Analyzing…' : 'Analyze'}
        </Button>
      </form>

      {analyze.isError && (
        <p className='text-destructive'>
          Analysis failed. Check that the Scrapy pipeline has populated at least
          a few models.
        </p>
      )}

      {result && (
        <>
          <div className='mb-4 rounded-lg border p-4 text-sm'>
            <div className='mb-2 font-medium'>
              Extracted requirements{' '}
              <Badge variant='outline'>{result.requirementsSource}</Badge>
            </div>
            <div className='flex flex-wrap gap-2'>
              <Badge variant='secondary'>tier: {result.requirements.qualityTier}</Badge>
              <Badge variant='secondary'>modality: {result.requirements.modality}</Badge>
              {result.requirements.requireTools && <Badge>tools</Badge>}
              {result.requirements.requireVision && <Badge>vision</Badge>}
              {result.requirements.requireJson && <Badge>json</Badge>}
              {result.requirements.minContextWindow && (
                <Badge variant='secondary'>
                  ≥ {result.requirements.minContextWindow.toLocaleString()} tokens
                </Badge>
              )}
            </div>
          </div>

          {result.savings && (
            <Card className='mb-4 border-primary'>
              <CardHeader>
                <CardTitle>Projected savings vs. {result.savings.currentModelSlug}</CardTitle>
              </CardHeader>
              <CardContent className='grid grid-cols-3 gap-4 text-sm'>
                <div>
                  <div className='text-xs text-muted-foreground'>Current / month</div>
                  <div className='text-lg font-bold'>{formatUSD(result.savings.currentMonthlyCost)}</div>
                </div>
                <div>
                  <div className='text-xs text-muted-foreground'>Recommended / month</div>
                  <div className='text-lg font-bold'>{formatUSD(result.savings.recommendedMonthlyCost)}</div>
                </div>
                <div>
                  <div className='text-xs text-muted-foreground'>Annual savings</div>
                  <div className='text-lg font-bold text-green-600'>
                    {formatUSD(result.savings.annualSavings)} ({result.savings.savingsPercent.toFixed(1)}%)
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <div className='space-y-3'>
            {result.recommendations.map((r, i) => (
              <RecommendationCard key={r.id} item={r} isTop={i === 0} />
            ))}
            {result.recommendations.length === 0 && (
              <p className='text-muted-foreground'>
                No candidate models matched. Try relaxing requirements or check
                whether the Scrapy pipeline has run.
              </p>
            )}
          </div>
        </>
      )}
    </>
  )
}
