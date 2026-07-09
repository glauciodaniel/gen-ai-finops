import { axios } from '@/lib/axios-client'
import { useMutation } from '@tanstack/react-query'
import type {
  OptimizerRequest,
  OptimizerResult,
} from '@/features/pricing/types'

export function useOptimizerAnalyze() {
  return useMutation({
    mutationFn: async (payload: OptimizerRequest) => {
      const { data } = await axios.post<OptimizerResult>(
        '/optimizer/analyze',
        payload,
      )
      return data
    },
  })
}
