import { PageTitle } from '@/components/custom/page-title'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { useStats } from '@/features/pricing/api'
import { Link } from 'react-router-dom'

export default function Page() {
  const { data, isLoading } = useStats()

  return (
    <>
      <PageTitle title='Pricing Overview' />

      <div className='my-4 grid gap-4 md:grid-cols-4'>
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>
              Active Models
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold'>
              {isLoading ? '…' : (data?.activeModels ?? 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>
              Providers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold'>
              {isLoading ? '…' : (data?.providers ?? 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>
              Price Records
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold'>
              {isLoading ? '…' : (data?.priceRecords ?? 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>
              Last Scrape
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-sm font-medium'>
              {isLoading
                ? '…'
                : data?.lastScrapeAt
                  ? new Date(data.lastScrapeAt).toLocaleString()
                  : 'never'}
            </div>
            {data?.lastScrapeStatus && (
              <div className='mt-1 text-xs text-muted-foreground'>
                status: {data.lastScrapeStatus}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className='grid gap-4 md:grid-cols-3'>
        <Link to='/pricing/models'>
          <Card className='cursor-pointer transition hover:shadow-md'>
            <CardHeader>
              <CardTitle>Models</CardTitle>
            </CardHeader>
            <CardContent className='text-sm text-muted-foreground'>
              Browse and filter all active AI models with current pricing per 1M
              tokens.
            </CardContent>
          </Card>
        </Link>
        <Link to='/pricing/history'>
          <Card className='cursor-pointer transition hover:shadow-md'>
            <CardHeader>
              <CardTitle>Price History</CardTitle>
            </CardHeader>
            <CardContent className='text-sm text-muted-foreground'>
              Time-series chart of input and output pricing for a specific
              model.
            </CardContent>
          </Card>
        </Link>
        <Link to='/pricing/scrape-runs'>
          <Card className='cursor-pointer transition hover:shadow-md'>
            <CardHeader>
              <CardTitle>Scrape Runs</CardTitle>
            </CardHeader>
            <CardContent className='text-sm text-muted-foreground'>
              Audit log of every ingest batch — see partial/failed runs and
              their errors.
            </CardContent>
          </Card>
        </Link>
      </div>
    </>
  )
}
