import { PageTitle } from '@/components/custom/page-title'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useModels, useProviders } from '@/features/pricing/api'
import type { AiModelWithPrice } from '@/features/pricing/types'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

const MODALITIES = ['text', 'embedding', 'image', 'audio'] as const

function formatPrice(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  const n = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(n)) return '—'
  return `$${n.toFixed(n < 1 ? 4 : 2)}`
}

function CapabilityBadges({ model }: { model: AiModelWithPrice }) {
  const caps: string[] = []
  if (model.supports_tools) caps.push('tools')
  if (model.supports_vision) caps.push('vision')
  if (model.supports_json) caps.push('json')
  if (!caps.length) return <span className='text-muted-foreground'>—</span>
  return (
    <div className='flex flex-wrap gap-1'>
      {caps.map((c) => (
        <Badge key={c} variant='secondary'>
          {c}
        </Badge>
      ))}
    </div>
  )
}

export default function Page() {
  const [provider, setProvider] = useState<string>('all')
  const [modality, setModality] = useState<string>('all')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const limit = 20

  const { data: providers } = useProviders()
  const { data, isLoading } = useModels({
    provider: provider === 'all' ? undefined : provider,
    modality: modality === 'all' ? undefined : modality,
    page,
    limit,
  })

  const filtered = useMemo(() => {
    if (!data) return []
    if (!search) return data.items
    const q = search.toLowerCase()
    return data.items.filter(
      (m) =>
        m.slug.toLowerCase().includes(q) ||
        m.display_name.toLowerCase().includes(q),
    )
  }, [data, search])

  return (
    <>
      <PageTitle title='AI Models' />

      <div className='my-4 flex flex-wrap gap-2'>
        <Input
          placeholder='Search by slug or name…'
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className='max-w-xs'
        />
        <Select value={provider} onValueChange={(v) => { setProvider(v); setPage(1) }}>
          <SelectTrigger className='w-48'>
            <SelectValue placeholder='Provider' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All providers</SelectItem>
            {providers?.map((p) => (
              <SelectItem key={p.slug} value={p.slug}>
                {p.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={modality} onValueChange={(v) => { setModality(v); setPage(1) }}>
          <SelectTrigger className='w-40'>
            <SelectValue placeholder='Modality' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All modalities</SelectItem>
            {MODALITIES.map((m) => (
              <SelectItem key={m} value={m}>
                {m}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className='rounded-lg border'>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Provider</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Modality</TableHead>
              <TableHead className='text-right'>Input / 1M</TableHead>
              <TableHead className='text-right'>Output / 1M</TableHead>
              <TableHead className='text-right'>Context</TableHead>
              <TableHead>Capabilities</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={8} className='text-center text-muted-foreground py-8'>
                  Loading…
                </TableCell>
              </TableRow>
            )}
            {!isLoading && filtered.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} className='text-center text-muted-foreground py-8'>
                  No models found. Has the Scrapy pipeline run yet?
                </TableCell>
              </TableRow>
            )}
            {filtered.map((m) => {
              const price = m.prices?.[0]
              return (
                <TableRow key={m.id}>
                  <TableCell>{m.provider.name}</TableCell>
                  <TableCell>
                    <div className='font-medium'>{m.display_name}</div>
                    <div className='text-xs text-muted-foreground'>{m.slug}</div>
                  </TableCell>
                  <TableCell>
                    <Badge variant='outline'>{m.modality}</Badge>
                  </TableCell>
                  <TableCell className='text-right font-mono'>
                    {formatPrice(price?.input_per_1m)}
                  </TableCell>
                  <TableCell className='text-right font-mono'>
                    {formatPrice(price?.output_per_1m)}
                  </TableCell>
                  <TableCell className='text-right'>
                    {m.context_window?.toLocaleString() ?? '—'}
                  </TableCell>
                  <TableCell>
                    <CapabilityBadges model={m} />
                  </TableCell>
                  <TableCell>
                    <Link
                      to={`/pricing/history?slug=${encodeURIComponent(m.slug)}`}
                      className='text-primary underline text-sm'
                    >
                      history
                    </Link>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </div>

      {data && data.pages > 1 && (
        <div className='mt-4 flex items-center justify-between text-sm'>
          <div className='text-muted-foreground'>
            Page {data.page} of {data.pages} — {data.total} models
          </div>
          <div className='flex gap-2'>
            <Button
              variant='outline'
              size='sm'
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <Button
              variant='outline'
              size='sm'
              disabled={page >= data.pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </>
  )
}
