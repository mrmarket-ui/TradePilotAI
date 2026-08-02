import { useMutation } from "@tanstack/react-query"

import { scoreSetup } from "@/api/setupScore"

import type {
  SetupScorePayload,
} from "@/types/setupScore"

export function useSetupScore() {
  const mutation = useMutation({
    mutationFn: ({
      strategyId,
      payload,
    }: {
      strategyId: number
      payload: SetupScorePayload
    }) =>
      scoreSetup(
        strategyId,
        payload,
      ),
  })

  return {
    scoreSetup:
      mutation.mutateAsync,

    result:
      mutation.data,

    error:
      mutation.error,

    isScoring:
      mutation.isPending,

    reset:
      mutation.reset,
  }
}
