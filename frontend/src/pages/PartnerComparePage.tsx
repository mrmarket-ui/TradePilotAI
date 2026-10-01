import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react"
import { useQuery } from "@tanstack/react-query"
import {
  ArrowLeftRight,
  Check,
  ChevronDown,
  Search,
} from "lucide-react"

import {
  getPartners,
  type Partner,
} from "@/api/partners"

type PartnerSelectorProps = {
  label: string
  partners: Partner[]
  value: number | null
  excludedId: number | null
  onChange: (value: number | null) => void
}

function PartnerSelector({
  label,
  partners,
  value,
  excludedId,
  onChange,
}: PartnerSelectorProps) {
  const [open, setOpen] =
    useState(false)

  const [search, setSearch] =
    useState("")

  const rootRef =
    useRef<HTMLDivElement | null>(null)

  const selected =
    partners.find(
      (partner) =>
        partner.id === value,
    ) || null

  const filtered = useMemo(() => {
    const query =
      search.trim().toLowerCase()

    return partners.filter(
      (partner) => {
        if (
          excludedId &&
          partner.id === excludedId
        ) {
          return false
        }

        if (!query) {
          return true
        }

        return (
          partner.name
            .toLowerCase()
            .includes(query) ||
          partner.category
            .replace("_", " ")
            .toLowerCase()
            .includes(query)
        )
      },
    )
  }, [
    excludedId,
    partners,
    search,
  ])

  useEffect(() => {
    function handleOutsideClick(
      event: MouseEvent,
    ) {
      if (
        rootRef.current &&
        !rootRef.current.contains(
          event.target as Node,
        )
      ) {
        setOpen(false)
      }
    }

    document.addEventListener(
      "mousedown",
      handleOutsideClick,
    )

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick,
      )
    }
  }, [])

  function selectPartner(
    partner: Partner,
  ) {
    onChange(partner.id)
    setOpen(false)
    setSearch("")
  }

  return (
    <div
      ref={rootRef}
      className={
        open
          ? "relative z-[100]"
          : "relative z-10"
      }
    >
      <button
        type="button"
        onClick={() =>
          setOpen((current) => !current)
        }
        className={[
          "flex w-full items-center justify-between gap-3",
          "rounded-2xl border px-4 py-3.5 text-left",
          "transition",
          open
            ? "border-blue-400/40 bg-[#101827] ring-4 ring-blue-500/[0.06]"
            : "border-white/[0.08] bg-[#0b1120] hover:border-white/[0.14] hover:bg-[#101827]",
        ].join(" ")}
      >
        <div className="min-w-0">
          {selected ? (
            <>
              <p className="truncate text-sm font-semibold text-white">
                {selected.name}
              </p>

              <p className="mt-0.5 text-[11px] uppercase tracking-[0.16em] text-slate-500">
                {selected.category.replace(
                  "_",
                  " ",
                )}
              </p>
            </>
          ) : (
            <p className="text-sm text-slate-400">
              {label}
            </p>
          )}
        </div>

        <ChevronDown
          className={[
            "size-4 shrink-0 text-slate-500 transition-transform",
            open
              ? "rotate-180"
              : "",
          ].join(" ")}
        />
      </button>

      {open ? (
        <div className="absolute left-0 right-0 z-[110] mt-2 overflow-hidden rounded-3xl border border-white/[0.1] bg-[#0b1120]/98 p-2 shadow-2xl shadow-black/50 backdrop-blur-xl">
          <div className="flex items-center gap-2 rounded-2xl border border-white/[0.08] bg-white/[0.03] px-3">
            <Search className="size-4 text-slate-500" />

            <input
              autoFocus
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
              }
              placeholder="Search providers..."
              className="h-11 w-full bg-transparent text-sm text-slate-200 outline-none placeholder:text-slate-600"
            />
          </div>

          <div className="mt-2 max-h-72 space-y-1 overflow-y-auto pr-1">
            {selected ? (
              <button
                type="button"
                onClick={() => {
                  onChange(null)
                  setOpen(false)
                  setSearch("")
                }}
                className="flex w-full items-center rounded-2xl px-3 py-3 text-left text-sm text-slate-500 transition hover:bg-white/[0.04] hover:text-slate-300"
              >
                Clear selection
              </button>
            ) : null}

            {filtered.map(
              (partner) => {
                const isSelected =
                  partner.id === value

                return (
                  <button
                    key={partner.id}
                    type="button"
                    onClick={() =>
                      selectPartner(
                        partner,
                      )
                    }
                    className={[
                      "flex w-full items-center justify-between gap-3 rounded-2xl px-3 py-3 text-left transition",
                      isSelected
                        ? "bg-blue-500/12 text-blue-200 ring-1 ring-blue-400/15"
                        : "text-slate-300 hover:bg-white/[0.05] hover:text-white",
                    ].join(" ")}
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">
                        {partner.name}
                      </p>

                      <p className="mt-1 text-[10px] uppercase tracking-[0.15em] text-slate-600">
                        {partner.category.replace(
                          "_",
                          " ",
                        )}
                      </p>
                    </div>

                    {isSelected ? (
                      <span className="grid size-7 shrink-0 place-items-center rounded-xl bg-blue-500/15 text-blue-300">
                        <Check className="size-4" />
                      </span>
                    ) : null}
                  </button>
                )
              },
            )}

            {filtered.length ===
            0 ? (
              <div className="px-4 py-8 text-center text-sm text-slate-500">
                No providers found.
              </div>
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default function PartnerComparePage() {
  const query = useQuery({
    queryKey: ["partners"],
    queryFn: () =>
      getPartners(),
  })

  const [
    leftId,
    setLeftId,
  ] = useState<number | null>(
    null,
  )

  const [
    rightId,
    setRightId,
  ] = useState<number | null>(
    null,
  )

  const partners =
    query.data || []

  const left = useMemo(
    () =>
      partners.find(
        (partner) =>
          partner.id === leftId,
      ) || null,
    [partners, leftId],
  )

  const right = useMemo(
    () =>
      partners.find(
        (partner) =>
          partner.id === rightId,
      ) || null,
    [partners, rightId],
  )

  const rows = [
    [
      "Category",
      (partner: Partner) =>
        partner.category.replace(
          "_",
          " ",
        ),
    ],
    [
      "Minimum Deposit",
      (partner: Partner) =>
        partner.minimum_deposit ||
        "Not provided",
    ],
    [
      "Platforms",
      (partner: Partner) =>
        partner.platforms?.join(
          ", ",
        ) || "Not provided",
    ],
    [
      "Regulation",
      (partner: Partner) =>
        partner.regulation ||
        "Not provided",
    ],
    [
      "Challenge Size",
      (partner: Partner) =>
        partner.challenge_size ||
        "N/A",
    ],
    [
      "Challenge Fee",
      (partner: Partner) =>
        partner.challenge_fee ||
        "N/A",
    ],
    [
      "Profit Split",
      (partner: Partner) =>
        partner.profit_split ||
        "N/A",
    ],
    [
      "Max Drawdown",
      (partner: Partner) =>
        partner.max_drawdown ||
        "N/A",
    ],
    [
      "Payout Frequency",
      (partner: Partner) =>
        partner.payout_frequency ||
        "Not provided",
    ],
  ] as const

  function changeLeft(
    nextId: number | null,
  ) {
    setLeftId(nextId)

    if (
      nextId !== null &&
      rightId === nextId
    ) {
      setRightId(null)
    }
  }

  function changeRight(
    nextId: number | null,
  ) {
    setRightId(nextId)

    if (
      nextId !== null &&
      leftId === nextId
    ) {
      setLeftId(null)
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.25em] text-blue-300">
          Partner Comparison
        </p>

        <h1 className="mt-2 text-3xl font-semibold text-white">
          Compare Brokers & Prop Firms
        </h1>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Compare key provider details
          side-by-side before visiting a
          broker or prop firm.
        </p>
      </header>

      {query.isLoading ? (
        <div className="premium-card rounded-3xl p-8 text-center text-sm text-slate-500">
          Loading providers...
        </div>
      ) : query.isError ? (
        <div className="rounded-3xl border border-red-400/20 bg-red-400/[0.05] p-6 text-sm text-red-300">
          Partner data could not be
          loaded. Please try again.
        </div>
      ) : (
        <>
          <section className="relative z-30 premium-card rounded-[2rem] p-5 md:p-6">
            <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr] md:items-center">
              <PartnerSelector
                label="Choose first partner"
                partners={partners}
                value={leftId}
                excludedId={rightId}
                onChange={changeLeft}
              />

              <div className="hidden md:grid">
                <div className="grid size-11 place-items-center rounded-2xl border border-white/[0.08] bg-white/[0.03] text-slate-500">
                  <ArrowLeftRight className="size-5" />
                </div>
              </div>

              <PartnerSelector
                label="Choose second partner"
                partners={partners}
                value={rightId}
                excludedId={leftId}
                onChange={changeRight}
              />
            </div>
          </section>

          {left && right ? (
            <section className="relative z-0 premium-card overflow-hidden rounded-[2rem]">
              <div className="border-b border-white/[0.07] px-5 py-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Comparison
                </p>

                <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
                  <span className="font-semibold text-white">
                    {left.name}
                  </span>

                  <ArrowLeftRight className="size-4 text-blue-300" />

                  <span className="font-semibold text-white">
                    {right.name}
                  </span>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px]">
                  <thead>
                    <tr className="bg-white/[0.02]">
                      <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-600">
                        Feature
                      </th>

                      <th className="px-5 py-4 text-left text-sm font-semibold text-white">
                        {left.name}
                      </th>

                      <th className="px-5 py-4 text-left text-sm font-semibold text-white">
                        {right.name}
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {rows.map(
                      ([
                        label,
                        getValue,
                      ]) => (
                        <tr
                          key={label}
                          className="border-t border-white/[0.06] transition hover:bg-white/[0.015]"
                        >
                          <td className="px-5 py-4 text-sm font-medium text-slate-500">
                            {label}
                          </td>

                          <td className="px-5 py-4 text-sm text-slate-300">
                            {getValue(
                              left,
                            )}
                          </td>

                          <td className="px-5 py-4 text-sm text-slate-300">
                            {getValue(
                              right,
                            )}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          ) : (
            <section className="relative z-0 premium-card rounded-[2rem] p-10 text-center">
              <div className="mx-auto grid size-14 place-items-center rounded-2xl border border-white/[0.07] bg-white/[0.025]">
                <ArrowLeftRight className="size-6 text-slate-500" />
              </div>

              <h2 className="mt-4 font-semibold text-slate-300">
                Select two providers
              </h2>

              <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500">
                Choose two different
                brokers or prop firms to
                compare their available
                details.
              </p>
            </section>
          )}
        </>
      )}
    </div>
  )
}
