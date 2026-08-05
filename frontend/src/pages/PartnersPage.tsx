import {
  Bookmark,
  Building2,
  Search,
  Star,
  Trophy,
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
  getPartners,
  getSavedPartners,
  savePartner,
  trackPartnerClick,
  unsavePartner,
  type Partner,
} from "@/api/partners"
import PartnerCard from "@/components/partners/PartnerCard"

type Filter =
  | "all"
  | "broker"
  | "prop_firm"
  | "saved"

export default function PartnersPage() {
  const qc = useQueryClient()

  const [filter, setFilter] =
    useState<Filter>("all")

  const [search, setSearch] =
    useState("")

  const partnersQuery = useQuery({
    queryKey: ["partners"],
    queryFn: () => getPartners(),
  })

  const savedQuery = useQuery({
    queryKey: ["partners", "saved"],
    queryFn: getSavedPartners,
  })

  const savedIds = useMemo(
    () =>
      new Set(
        (savedQuery.data || []).map(
          partner => partner.id,
        ),
      ),
    [savedQuery.data],
  )

  const saveMutation = useMutation({
    mutationFn: async (
      partner: Partner,
    ) => {
      if (savedIds.has(partner.id)) {
        return unsavePartner(partner.id)
      }

      return savePartner(partner.id)
    },

    onSuccess: async () => {
      await qc.invalidateQueries({
        queryKey: ["partners", "saved"],
      })
    },
  })

  const filtered = useMemo(() => {
    const term =
      search.trim().toLowerCase()

    return (partnersQuery.data || []).filter(
      partner => {
        if (
          filter === "broker" &&
          partner.category !== "broker"
        ) {
          return false
        }

        if (
          filter === "prop_firm" &&
          partner.category !== "prop_firm"
        ) {
          return false
        }

        if (
          filter === "saved" &&
          !savedIds.has(partner.id)
        ) {
          return false
        }

        if (!term) return true

        return [
          partner.name,
          partner.description,
          partner.badge,
          partner.category,
        ]
          .filter(Boolean)
          .some(value =>
            String(value)
              .toLowerCase()
              .includes(term),
          )
      },
    )
  }, [
    partnersQuery.data,
    filter,
    search,
    savedIds,
  ])

  const featured = useMemo(
    () =>
      (partnersQuery.data || []).filter(
        partner => partner.featured,
      ),
    [partnersQuery.data],
  )

  async function openPartner(
    partner: Partner,
  ) {
    const newWindow = window.open(
      "",
      "_blank",
    )

    try {
      const result =
        await trackPartnerClick(
          partner.id,
          "partners_page",
        )

      const url =
        result.redirect_url ||
        partner.referral_url

      if (newWindow) {
        newWindow.opener = null
        newWindow.location.href = url
      } else {
        window.location.href = url
      }
    } catch {
      if (newWindow) {
        newWindow.opener = null
        newWindow.location.href =
          partner.referral_url
      } else {
        window.location.href =
          partner.referral_url
      }
    }
  }

  if (partnersQuery.isLoading) {
    return (
      <div className="p-8 text-slate-400">
        Loading partners...
      </div>
    )
  }

  if (partnersQuery.isError) {
    return (
      <div className="p-8">
        <div className="rounded-3xl border border-red-400/20 bg-red-400/10 p-6 text-red-200">
          Unable to load partner offers.
        </div>
      </div>
    )
  }

  const filters: {
    id: Filter
    label: string
    icon: typeof Building2
  }[] = [
    {
      id: "all",
      label: "All",
      icon: Star,
    },
    {
      id: "broker",
      label: "Brokers",
      icon: Building2,
    },
    {
      id: "prop_firm",
      label: "Prop Firms",
      icon: Trophy,
    },
    {
      id: "saved",
      label: "Saved",
      icon: Bookmark,
    },
  ]

  return (
    <div className="space-y-8">
      <header>
        <p className="text-xs uppercase tracking-[.25em] text-blue-300">
          TradePilot Partner Center
        </p>

        <h1 className="mt-2 text-3xl font-semibold">
          Brokers & Prop Firms
        </h1>

        <p className="mt-2 max-w-3xl text-slate-400">
          Discover trading partners, funding
          opportunities and offers available
          through TradePilot AI.
        </p>
      </header>

      {featured.length > 0 && (
        <section>
          <div className="mb-5 flex items-center gap-2">
            <Star className="size-5 text-amber-300" />

            <h2 className="text-xl font-semibold">
              Featured Offers
            </h2>
          </div>

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {featured.map(partner => (
              <PartnerCard
                key={partner.id}
                partner={partner}
                saved={savedIds.has(
                  partner.id,
                )}
                busy={
                  saveMutation.isPending
                }
                onOpen={openPartner}
                onSave={partner =>
                  saveMutation.mutate(
                    partner,
                  )
                }
              />
            ))}
          </div>
        </section>
      )}

      <section className="premium-card rounded-3xl p-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap gap-2">
            {filters.map(item => {
              const Icon = item.icon

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() =>
                    setFilter(item.id)
                  }
                  className={`flex items-center gap-2 rounded-2xl px-4 py-2 text-sm transition ${
                    filter === item.id
                      ? "bg-blue-500 text-white"
                      : "border border-white/10 text-slate-300 hover:bg-white/5"
                  }`}
                >
                  <Icon className="size-4" />
                  {item.label}
                </button>
              )
            })}
          </div>

          <div className="relative w-full xl:max-w-sm">
            <Search className="absolute left-4 top-1/2 size-4 -translate-y-1/2 text-slate-500" />

            <input
              value={search}
              onChange={event =>
                setSearch(
                  event.target.value,
                )
              }
              placeholder="Search partners..."
              className="w-full rounded-2xl border border-white/10 bg-white/[.03] py-3 pl-11 pr-4 outline-none transition focus:border-blue-400/50"
            />
          </div>
        </div>
      </section>

      <section>
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">
              {filter === "broker"
                ? "Broker Recommendations"
                : filter === "prop_firm"
                  ? "Prop Firm Opportunities"
                  : filter === "saved"
                    ? "Saved Partners"
                    : "All Partners"}
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              {filtered.length} offer
              {filtered.length === 1
                ? ""
                : "s"}
            </p>
          </div>
        </div>

        {filtered.length ? (
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {filtered.map(partner => (
              <PartnerCard
                key={partner.id}
                partner={partner}
                saved={savedIds.has(
                  partner.id,
                )}
                busy={
                  saveMutation.isPending
                }
                onOpen={openPartner}
                onSave={partner =>
                  saveMutation.mutate(
                    partner,
                  )
                }
              />
            ))}
          </div>
        ) : (
          <div className="premium-card rounded-3xl p-10 text-center text-slate-400">
            No partners match your search.
          </div>
        )}
      </section>

      <section className="rounded-3xl border border-amber-400/20 bg-amber-400/[.05] p-5 text-sm leading-6 text-slate-400">
        <strong className="text-amber-200">
          Affiliate disclosure:
        </strong>{" "}
        TradePilot AI may earn a commission
        when users register or purchase through
        partner links. Partner inclusion is not
        financial advice or a guarantee of
        trading performance. Trading and prop
        firm challenges involve risk.
      </section>
    </div>
  )
}
