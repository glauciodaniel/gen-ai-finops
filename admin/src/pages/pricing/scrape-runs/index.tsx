import { PageTitle } from '@/components/custom/page-title'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useScrapeRuns } from '@/features/pricing/api'
import type { ScrapeRun } from '@/features/pricing/types'

function statusVariant(
  status: ScrapeRun['status'],
): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'success':
      return 'default'
    case 'partial':
      return 'secondary'
    case 'failed':
      return 'destructive'
    default:
      return 'outline'
  }
}

function formatDuration(start: string, end: string | null): string {
  if (!end) return '—'
  const ms = new Date(end).getTime() - new Date(start).getTime()
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

export default function Page() {
  const { data, isLoading } = useScrapeRuns(50)

  return (
    <>
      <PageTitle title='Scrape Runs' />

      <p className='my-4 text-sm text-muted-foreground'>
        Audit log of every ingest batch received from the Scrapy pipeline. A{' '}
        <code>partial</code> or <code>failed</code> status means the run's error
        log has details worth checking.
      </p>

      <div className='rounded-lg border'>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Provider</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className='text-right'>Found</TableHead>
              <TableHead className='text-right'>Changed</TableHead>
              <TableHead>Started</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Errors</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell
                  colSpan={8}
                  className='py-8 text-center text-muted-foreground'
                >
                  Loading…
                </TableCell>
              </TableRow>
            )}
            {!isLoading && (!data || data.length === 0) && (
              <TableRow>
                <TableCell
                  colSpan={8}
                  className='py-8 text-center text-muted-foreground'
                >
                  No scrape runs yet.
                </TableCell>
              </TableRow>
            )}
            {data?.map((run) => (
              <TableRow key={run.id}>
                <TableCell className='font-mono'>#{run.id}</TableCell>
                <TableCell>{run.provider ?? '—'}</TableCell>
                <TableCell>
                  <Badge variant={statusVariant(run.status)}>{run.status}</Badge>
                </TableCell>
                <TableCell className='text-right'>{run.items_found}</TableCell>
                <TableCell className='text-right'>{run.items_changed}</TableCell>
                <TableCell>
                  {new Date(run.started_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {formatDuration(run.started_at, run.finished_at)}
                </TableCell>
                <TableCell className='max-w-md'>
                  {run.error_log ? (
                    <details>
                      <summary className='cursor-pointer text-sm text-destructive'>
                        view errors
                      </summary>
                      <pre className='mt-2 whitespace-pre-wrap text-xs'>
                        {run.error_log}
                      </pre>
                    </details>
                  ) : (
                    <span className='text-muted-foreground'>—</span>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </>
  )
}
