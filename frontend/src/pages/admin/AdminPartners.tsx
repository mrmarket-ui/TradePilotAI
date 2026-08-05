import {
  BarChart3,
  Edit3,
  Plus,
  Star,
} from "lucide-react"
import {
  useMemo,
  useState,
} from "react"
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  createAdminPartner,
  getAdminPartnerAnalytics,
  getAdminPartners,
  updateAdminPartner,
  updateAdminPartnerStatus,
} from "@/api/admin/partners"
import type { Partner } from "@/api/partners"

const emptyPartner = {
  name: "",
  slug: "",
  category: "broker",
  description: "",
  referral_url: "",
  badge: "",
  featured: false,
  display_order: 0,
}

export default function AdminPartners() {
  const qc = useQueryClient()

  const [editing, setEditing] =
    useState<Partner | null>(null)

  const [form, setForm] =
    useState<any>(emptyPartner)

  const [open, setOpen] =
    useState(false)

  const partnersQuery = useQuery({
    queryKey: ["admin-partners"],
    queryFn: getAdminPartners,
  })

  const analyticsQuery = useQuery({
    queryKey: ["admin-partners-analytics"],
    queryFn: () => getAdminPartnerAnalytics(30),
  })

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (editing) {
        return updateAdminPartner(
          editing.id,
          form,
        )
      }

      return createAdminPartner(
        form,
      )
    },

    onSuccess: async () => {
      setOpen(false)
      setEditing(null)
      setForm(emptyPartner)

      await qc.invalidateQueries({
        queryKey: ["admin-partners"],
      })

      await qc.invalidateQueries({
        queryKey: ["partners"],
      })
    },
  })

  const statusMutation = useMutation({
    mutationFn: ({
      id,
      status,
    }: {
      id: number
      status: string
    }) =>
      updateAdminPartnerStatus(
        id,
        status,
      ),

    onSuccess: async () => {
      await qc.invalidateQueries({
        queryKey: ["admin-partners"],
      })

      await qc.invalidateQueries({
        queryKey: ["partners"],
      })
    },
  })

  const clickMap = useMemo(() => {
    const map = new Map<number, number>()

    for (
      const item of
      analyticsQuery.data?.partners || []
    ) {
      map.set(
        item.partner_id,
        item.clicks,
      )
    }

    return map
  }, [analyticsQuery.data])

  function editPartner(
    partner: Partner,
  ) {
    setEditing(partner)

    setForm({
      ...partner,
    })

    setOpen(true)
  }

  function newPartner() {
    setEditing(null)
    setForm(emptyPartner)
    setOpen(true)
  }

  const stats = analyticsQuery.data

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[.25em] text-blue-300">
            Partner Management
          </p>

          <h1 className="mt-2 text-3xl font-semibold">
            Partners
          </h1>
        </div>

        <button
          type="button"
          onClick={newPartner}
          className="flex items-center gap-2 rounded-2xl bg-blue-500 px-5 py-3 font-medium"
        >
          <Plus className="size-4" />
          Add Partner
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {[
          [
            "Partners",
            stats?.total_partners || 0,
          ],
          [
            "Active",
            stats?.active_partners || 0,
          ],
          [
            "Clicks",
            stats?.total_clicks || 0,
          ],
          [
            "Saved",
            stats?.saved_count || 0,
          ],
        ].map(([label, value]) => (
          <div
            key={String(label)}
            className="premium-card rounded-3xl p-5"
          >
            <p className="text-sm text-slate-500">
              {label}
            </p>

            <p className="mt-3 text-3xl font-semibold">
              {String(value)}
            </p>
          </div>
        ))}
      </div>

      <div className="premium-card overflow-x-auto rounded-3xl">
        <table className="w-full min-w-[950px]">
          <thead>
            <tr>
              {[
                "Partner",
                "Category",
                "Status",
                "Featured",
                "Clicks",
                "Order",
                "Actions",
              ].map(item => (
                <th
                  key={item}
                  className="px-5 py-4 text-left text-xs uppercase text-slate-500"
                >
                  {item}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {(partnersQuery.data?.partners || []).map(
              partner => (
                <tr
                  key={partner.id}
                  className="border-t border-white/[.06]"
                >
                  <td className="px-5 py-4">
                    <b>{partner.name}</b>

                    <div className="text-xs text-slate-500">
                      {partner.slug}
                    </div>
                  </td>

                  <td className="px-5 py-4 capitalize">
                    {partner.category.replace(
                      "_",
                      " ",
                    )}
                  </td>

                  <td className="px-5 py-4">
                    <select
                      value={partner.status}
                      onChange={event =>
                        statusMutation.mutate({
                          id: partner.id,
                          status:
                            event.target.value,
                        })
                      }
                      className="rounded-xl bg-[#0b1120] px-3 py-2"
                    >
                      <option value="active">
                        Active
                      </option>

                      <option value="paused">
                        Paused
                      </option>

                      <option value="coming_soon">
                        Coming Soon
                      </option>

                      <option value="expired">
                        Expired
                      </option>
                    </select>
                  </td>

                  <td className="px-5 py-4">
                    {partner.featured ? (
                      <Star className="size-5 fill-current text-amber-300" />
                    ) : (
                      "—"
                    )}
                  </td>

                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="size-4 text-blue-300" />

                      {clickMap.get(
                        partner.id,
                      ) || 0}
                    </div>
                  </td>

                  <td className="px-5 py-4">
                    {partner.display_order}
                  </td>

                  <td className="px-5 py-4">
                    <button
                      type="button"
                      onClick={() =>
                        editPartner(partner)
                      }
                      className="rounded-xl border border-white/10 p-2 hover:bg-white/5"
                    >
                      <Edit3 className="size-4" />
                    </button>
                  </td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4">
          <div className="premium-card max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-3xl p-7">
            <h2 className="text-2xl font-semibold">
              {editing
                ? "Edit Partner"
                : "Add Partner"}
            </h2>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <input
                placeholder="Name"
                value={form.name}
                onChange={event =>
                  setForm({
                    ...form,
                    name:
                      event.target.value,
                  })
                }
                className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
              />

              <input
                placeholder="Slug"
                value={form.slug}
                onChange={event =>
                  setForm({
                    ...form,
                    slug:
                      event.target.value,
                  })
                }
                className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
              />

              <select
                value={form.category}
                onChange={event =>
                  setForm({
                    ...form,
                    category:
                      event.target.value,
                  })
                }
                className="rounded-2xl bg-[#0b1120] px-4 py-3"
              >
                <option value="broker">
                  Broker
                </option>

                <option value="prop_firm">
                  Prop Firm
                </option>
              </select>

              <input
                placeholder="Badge"
                value={form.badge || ""}
                onChange={event =>
                  setForm({
                    ...form,
                    badge:
                      event.target.value,
                  })
                }
                className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
              />

              <input
                type="number"
                placeholder="Display order"
                value={form.display_order}
                onChange={event =>
                  setForm({
                    ...form,
                    display_order:
                      Number(
                        event.target.value,
                      ),
                  })
                }
                className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
              />

              <label className="flex items-center gap-3 rounded-2xl border border-white/10 px-4 py-3">
                <input
                  type="checkbox"
                  checked={
                    Boolean(form.featured)
                  }
                  onChange={event =>
                    setForm({
                      ...form,
                      featured:
                        event.target.checked,
                    })
                  }
                />

                Featured
              </label>
            </div>

            <textarea
              rows={4}
              placeholder="Description"
              value={form.description || ""}
              onChange={event =>
                setForm({
                  ...form,
                  description:
                    event.target.value,
                })
              }
              className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
            />

            <input
              placeholder="Referral URL"
              value={form.referral_url}
              onChange={event =>
                setForm({
                  ...form,
                  referral_url:
                    event.target.value,
                })
              }
              className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
            />

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() =>
                  setOpen(false)
                }
                className="rounded-2xl border border-white/10 px-5 py-3"
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={
                  saveMutation.isPending
                }
                onClick={() =>
                  saveMutation.mutate()
                }
                className="rounded-2xl bg-blue-500 px-5 py-3 font-medium disabled:opacity-50"
              >
                {saveMutation.isPending
                  ? "Saving..."
                  : "Save Partner"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

