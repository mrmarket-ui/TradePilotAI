import { useQuery } from "@tanstack/react-query"

import {
  getAdminSubscriptions,
} from "@/api/admin/admin"

export default function AdminSubscriptions() {
  const query = useQuery({
    queryKey: ["admin-subscriptions"],
    queryFn: getAdminSubscriptions,
  })

  return (
    <div>
      <h1 className="text-3xl font-semibold">
        Subscriptions
      </h1>

      <p className="mt-2 text-slate-500">
        Monitor PayPal subscription records.
      </p>

      <div className="mt-6 space-y-4">
        {query.data?.subscriptions.map(
          (subscription) => (
            <div
              key={subscription.id}
              className="premium-card rounded-3xl p-5"
            >
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div>
                  <p className="text-xs text-slate-500">
                    User
                  </p>
                  <p className="mt-1">
                    #{subscription.user_id}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-500">
                    Plan
                  </p>
                  <p className="mt-1 capitalize">
                    {subscription.plan}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-500">
                    Status
                  </p>
                  <p className="mt-1 capitalize">
                    {subscription.status}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-500">
                    Amount
                  </p>
                  <p className="mt-1">
                    {subscription.amount
                      ? `${subscription.currency} ${subscription.amount}`
                      : "—"}
                  </p>
                </div>
              </div>

              <div className="mt-4 text-sm text-slate-500">
                {subscription.payer_email || "No payer email"}
              </div>

              <div className="mt-2 break-all text-xs text-slate-600">
                {subscription.paypal_subscription_id || "No PayPal subscription ID"}
              </div>
            </div>
          ),
        )}
      </div>
    </div>
  )
}
