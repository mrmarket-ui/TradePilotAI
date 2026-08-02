import { useQuery } from "@tanstack/react-query"

import {
  getAdminHealth,
  getAdminWebhooks,
} from "@/api/admin/admin"

export default function AdminSystem() {
  const health = useQuery({
    queryKey: ["admin-health"],
    queryFn: getAdminHealth,
  })

  const webhooks = useQuery({
    queryKey: ["admin-webhooks"],
    queryFn: getAdminWebhooks,
  })

  return (
    <div>
      <h1 className="text-3xl font-semibold">
        System
      </h1>

      <p className="mt-2 text-slate-500">
        Monitor infrastructure and PayPal webhooks.
      </p>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <div className="premium-card rounded-3xl p-6">
          <p className="text-sm text-slate-500">
            API
          </p>

          <p className="mt-2 text-2xl font-semibold">
            {health.data?.api || "checking"}
          </p>
        </div>

        <div className="premium-card rounded-3xl p-6">
          <p className="text-sm text-slate-500">
            Database
          </p>

          <p className="mt-2 text-2xl font-semibold">
            {health.data?.database || "checking"}
          </p>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold">
          Recent PayPal Webhooks
        </h2>

        <div className="mt-4 space-y-3">
          {webhooks.data?.events.map(
            (event) => (
              <div
                key={event.id}
                className="premium-card rounded-2xl p-4"
              >
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-medium">
                      {event.event_type}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {event.paypal_event_id}
                    </p>
                  </div>

                  <span className="text-sm capitalize">
                    {event.processing_status}
                  </span>
                </div>

                {event.error_message ? (
                  <p className="mt-3 text-sm text-red-300">
                    {event.error_message}
                  </p>
                ) : null}
              </div>
            ),
          )}
        </div>
      </div>
    </div>
  )
}
