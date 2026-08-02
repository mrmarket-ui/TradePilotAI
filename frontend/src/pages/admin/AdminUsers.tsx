import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"
import { useState } from "react"

import {
  changeAdminUserCredits,
  changeAdminUserPlan,
  changeAdminUserStatus,
  getAdminUsers,
} from "@/api/admin/admin"

export default function AdminUsers() {
  const [search, setSearch] = useState("")
  const client = useQueryClient()

  const query = useQuery({
    queryKey: ["admin-users", search],
    queryFn: () => getAdminUsers(search),
  })

  const refresh = () =>
    client.invalidateQueries({
      queryKey: ["admin-users"],
    })

  const planMutation = useMutation({
    mutationFn: ({
      id,
      plan,
    }: {
      id: number
      plan: "free" | "pro" | "premium"
    }) =>
      changeAdminUserPlan(id, plan),
    onSuccess: refresh,
  })

  const statusMutation = useMutation({
    mutationFn: ({
      id,
      active,
    }: {
      id: number
      active: boolean
    }) =>
      changeAdminUserStatus(id, active),
    onSuccess: refresh,
  })

  const creditsMutation = useMutation({
    mutationFn: ({
      id,
      credits,
    }: {
      id: number
      credits: number
    }) =>
      changeAdminUserCredits(
        id,
        credits,
      ),
    onSuccess: refresh,
  })

  return (
    <div>
      <h1 className="text-3xl font-semibold">
        Users
      </h1>

      <p className="mt-2 text-slate-500">
        Manage platform users, plans and access.
      </p>

      <input
        value={search}
        onChange={(event) =>
          setSearch(event.target.value)
        }
        placeholder="Search email, name or username"
        className="mt-6 w-full max-w-xl rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 outline-none"
      />

      <div className="mt-6 space-y-4">
        {query.data?.users.map((user) => (
          <div
            key={user.id}
            className="premium-card rounded-3xl p-5"
          >
            <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <p className="font-semibold">
                  {user.email}
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  ID {user.id}
                  {" · "}
                  {user.full_name || user.username || "No profile name"}
                </p>

                <p className="mt-2 text-sm">
                  Credits: {user.ai_credits}
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <select
                  value={user.plan}
                  onChange={(event) =>
                    planMutation.mutate({
                      id: user.id,
                      plan: event.target.value as
                        | "free"
                        | "pro"
                        | "premium",
                    })
                  }
                  className="rounded-xl border border-white/10 bg-[#0b1120] px-3 py-2"
                >
                  <option value="free">
                    Free
                  </option>
                  <option value="pro">
                    Pro
                  </option>
                  <option value="premium">
                    Premium
                  </option>
                </select>

                <button
                  type="button"
                  onClick={() =>
                    statusMutation.mutate({
                      id: user.id,
                      active: !user.is_active,
                    })
                  }
                  className="rounded-xl bg-white/[0.06] px-4 py-2"
                >
                  {user.is_active
                    ? "Suspend"
                    : "Activate"}
                </button>

                <button
                  type="button"
                  onClick={() =>
                    creditsMutation.mutate({
                      id: user.id,
                      credits: 1000,
                    })
                  }
                  className="rounded-xl bg-blue-500/15 px-4 py-2 text-blue-300"
                >
                  Give 1000 Credits
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
