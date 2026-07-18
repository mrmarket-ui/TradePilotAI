import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  activateStrategy,
  createStrategy,
  deleteStrategy,
  fetchStrategies,
  scoreStrategySetup,
  updateStrategy,
} from "@/api/strategy"

import type {
  SetupScorePayload,
  StrategyCreatePayload,
  StrategyUpdatePayload,
} from "@/types/strategy"


export function useStrategies() {
  const queryClient = useQueryClient()

  const strategiesQuery = useQuery({
    queryKey: ["strategies"],
    queryFn: fetchStrategies,
  })


  const createMutation = useMutation({
    mutationFn: (
      payload: StrategyCreatePayload,
    ) => createStrategy(payload),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["strategies"],
      })
    },
  })


  const updateMutation = useMutation({
    mutationFn: ({
      strategyId,
      payload,
    }: {
      strategyId: number
      payload: StrategyUpdatePayload
    }) =>
      updateStrategy(
        strategyId,
        payload,
      ),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["strategies"],
      })
    },
  })


  const deleteMutation = useMutation({
    mutationFn: (
      strategyId: number,
    ) => deleteStrategy(strategyId),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["strategies"],
      })
    },
  })


  const activateMutation = useMutation({
    mutationFn: (
      strategyId: number,
    ) => activateStrategy(strategyId),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["strategies"],
      })
    },
  })


  const scoreMutation = useMutation({
    mutationFn: ({
      strategyId,
      payload,
    }: {
      strategyId: number
      payload: SetupScorePayload
    }) =>
      scoreStrategySetup(
        strategyId,
        payload,
      ),
  })


  return {
    strategies:
      strategiesQuery.data?.strategies ?? [],

    total:
      strategiesQuery.data?.total ?? 0,

    isLoading:
      strategiesQuery.isLoading,

    isError:
      strategiesQuery.isError,

    error:
      strategiesQuery.error,

    refetch:
      strategiesQuery.refetch,

    createStrategy:
      createMutation.mutateAsync,

    updateStrategy:
      updateMutation.mutateAsync,

    deleteStrategy:
      deleteMutation.mutateAsync,

    activateStrategy:
      activateMutation.mutateAsync,

    scoreStrategy:
      scoreMutation.mutateAsync,

    isCreating:
      createMutation.isPending,

    isUpdating:
      updateMutation.isPending,

    isDeleting:
      deleteMutation.isPending,

    isActivating:
      activateMutation.isPending,

    isScoring:
      scoreMutation.isPending,

    scoreResult:
      scoreMutation.data,

    scoreError:
      scoreMutation.error,
  }
}
