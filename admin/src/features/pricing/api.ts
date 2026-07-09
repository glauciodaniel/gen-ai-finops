import { axios } from '@/lib/axios-client'
import { useQuery } from '@tanstack/react-query'
import type {
  ModelHistoryResponse,
  ModelsResponse,
  PricingStats,
  Provider,
  ScrapeRun,
} from './types'

export function useProviders() {
  return useQuery({
    queryKey: ['pricing', 'providers'],
    queryFn: async () => {
      const { data } = await axios.get<Provider[]>('/pricing/providers')
      return data
    },
  })
}

export function useModels(params: {
  provider?: string
  modality?: string
  page?: number
  limit?: number
}) {
  return useQuery({
    queryKey: ['pricing', 'models', params],
    queryFn: async () => {
      const { data } = await axios.get<ModelsResponse>('/pricing/models', {
        params,
      })
      return data
    },
    placeholderData: (previous) => previous,
  })
}

export function useModelHistory(slug: string | undefined, days = 30) {
  return useQuery({
    queryKey: ['pricing', 'history', slug, days],
    enabled: Boolean(slug),
    queryFn: async () => {
      const { data } = await axios.get<ModelHistoryResponse>(
        `/pricing/models/${slug}/history`,
        { params: { days } },
      )
      return data
    },
  })
}

export function useScrapeRuns(limit = 20) {
  return useQuery({
    queryKey: ['pricing', 'scrape-runs', limit],
    queryFn: async () => {
      const { data } = await axios.get<ScrapeRun[]>('/pricing/scrape-runs', {
        params: { limit },
      })
      return data
    },
  })
}

export function useStats() {
  return useQuery({
    queryKey: ['pricing', 'stats'],
    queryFn: async () => {
      const { data } = await axios.get<PricingStats>('/pricing/stats')
      return data
    },
  })
}
