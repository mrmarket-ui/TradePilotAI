import { useQuery } from "@tanstack/react-query"

import { mySubscription } from "@/api"

type SubscriptionPayload = {
  plan?: string
  status?: string
  next_billing_at?: string | null
}

export default function CurrentPlanText() {
  const query = useQuery<SubscriptionPayload>({
    queryKey: ["dashboard-current-plan"],
    queryFn: mySubscription,
  })

  if (query.isLoading) return <>Checking plan...</>

  if (query.isError || !query.data) return <>Plan unavailable</>

  const subscription = query.data

  const plan =
    subscription.status === "active" && subscription.plan
      ? subscription.plan
      : "free"

  if (plan === "free") return <>Free</>

  const name = plan.charAt(0).toUpperCase() + plan.slice(1)

  const renews = subscription.next_billing_at
    ? " \u00b7 renews " +
      new Date(subscription.next_billing_at).toLocaleDateString()
    : ""

  return <>{name + renews}</>
}