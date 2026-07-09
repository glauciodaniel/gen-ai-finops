import { PageTitle } from '@/components/custom/page-title'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useModelHistory } from '@/features/pricing/api'
import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const DAY_OPTIONS = [7, 30, 90, 180, 365] as const

export default function Page() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialSlug = searchParams.get('slug') ?? ''
  const [slug, setSlug] = useState(initialSlug)
  const [days, setDays] = useState<number>(30)

  const { data, isLoading, error } = useModelHistory(slug || undefined, days)

  const chartData = useMemo(() => {
    if (!data) return []
    return data.prices.map((p) => ({
      date: new Date(p.effective_from).toLocaleDateString(),
      input: Number(p.input_per_1m),
      output: Number(p.output_per_1m),
    }))
  }, [data])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const form = new FormData(e.target as HTMLFormElement)
    const nextSlug = String(form.get('slug') ?? '').trim()
    setSlug(nextSlug)
    if (nextSlug) setSearchParams({ slug: nextSlug })
  }

  return (
    <>
      <PageTitle title='Price History' />

      <form onSubmit={handleSubmit} className='my-4 flex flex-wrap gap-2'>
        <Input
          name='slug'
          placeholder='Model slug (e.g., gpt-4o)'
          defaultValue={slug}
          className='max-w-xs'
        />
        <Select value={String(days)} onValueChange={(v) => setDays(Number(v))}>
          <SelectTrigger className='w-32'>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {DAY_OPTIONS.map((d) => (
              <SelectItem key={d} value={String(d)}>
                Last {d} days
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </form>

      {!slug && (
        <p className='text-muted-foreground'>
          Enter a model slug above to see its price history.
        </p>
      )}

      {slug && isLoading && <p className='text-muted-foreground'>Loading…</p>}

      {slug && error && (
        <p className='text-destructive'>
          Could not load history for <code>{slug}</code>. Model not found?
        </p>
      )}

      {data && (
        <>
          <div className='mb-4'>
            <h2 className='text-lg font-semibold'>{data.model.display_name}</h2>
            <p className='text-sm text-muted-foreground'>
              {data.model.provider.name} · {data.prices.length} price record
              {data.prices.length === 1 ? '' : 's'} in the selected window
            </p>
          </div>

          <div className='rounded-lg border p-4' style={{ height: 400 }}>
            {chartData.length === 0 ? (
              <div className='flex h-full items-center justify-center text-muted-foreground'>
                No price records in this window.
              </div>
            ) : (
              <ResponsiveContainer width='100%' height='100%'>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray='3 3' />
                  <XAxis dataKey='date' />
                  <YAxis
                    label={{
                      value: 'USD per 1M tokens',
                      angle: -90,
                      position: 'insideLeft',
                    }}
                  />
                  <Tooltip />
                  <Legend />
                  <Line
                    type='monotone'
                    dataKey='input'
                    stroke='#2563eb'
                    strokeWidth={2}
                    dot
                  />
                  <Line
                    type='monotone'
                    dataKey='output'
                    stroke='#dc2626'
                    strokeWidth={2}
                    dot
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </>
      )}
    </>
  )
}
