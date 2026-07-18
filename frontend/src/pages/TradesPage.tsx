import { useMemo, useState, type FormEvent } from "react"
import {
  BrainCircuit,
  Pencil,
  Plus,
  Search,
  Trash2,
  X,
} from "lucide-react"
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  createTrade,
  deleteTrade,
  fetchTradeReview,
  fetchTrades,
  updateTrade,
} from "@/api/trades"

import type {
  Trade,
  TradePayload,
  TradeReview,
} from "@/types/trade"

const emptyForm = {
  broker: "Manual",
  ticket: "",
  pair: "XAUUSD",
  direction: "BUY" as "BUY" | "SELL",
  entry: "",
  exit_price: "",
  stop_loss: "",
  take_profit: "",
  lot_size: "",
  profit: "",
  strategy: "",
  emotion: "",
  notes: "",
}

export default function TradesPage() {
  const queryClient = useQueryClient()

  const [search, setSearch] = useState("")
  const [formOpen, setFormOpen] = useState(false)
  const [editingTrade, setEditingTrade] = useState<Trade | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [review, setReview] = useState<{
    trade: Trade
    data?: TradeReview
    loading?: boolean
    error?: string
  } | null>(null)

  const tradesQuery = useQuery({
    queryKey: ["trades"],
    queryFn: fetchTrades,
  })

  const createMutation = useMutation({
    mutationFn: createTrade,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["trades"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      setFormOpen(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: Partial<TradePayload>
    }) => updateTrade(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["trades"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      setFormOpen(false)
      setEditingTrade(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteTrade,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["trades"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })

  const trades = tradesQuery.data?.trades ?? []

  const filteredTrades = useMemo(() => {
    const query = search.trim().toLowerCase()

    if (!query) {
      return trades
    }

    return trades.filter((trade) =>
      [
        trade.pair,
        trade.strategy,
        trade.broker,
        trade.ticket,
        trade.notes,
      ]
        .filter(Boolean)
        .some((value) =>
          String(value).toLowerCase().includes(query),
        ),
    )
  }, [trades, search])

  function openNewTrade() {
    setEditingTrade(null)
    setForm(emptyForm)
    setFormOpen(true)
  }

  function openEditTrade(trade: Trade) {
    setEditingTrade(trade)

    setForm({
      broker: trade.broker ?? "",
      ticket: trade.ticket ?? "",
      pair: trade.pair,
      direction: trade.direction,
      entry: String(trade.entry),
      exit_price: String(trade.exit_price ?? ""),
      stop_loss: String(trade.stop_loss),
      take_profit: String(trade.take_profit),
      lot_size: String(trade.lot_size ?? ""),
      profit: String(trade.profit ?? ""),
      strategy: trade.strategy ?? "",
      emotion: trade.emotion ?? "",
      notes: trade.notes ?? "",
    })

    setFormOpen(true)
  }

  async function submitTrade(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const payload: TradePayload = {
      broker: form.broker.trim() || null,
      ticket: form.ticket.trim() || null,
      pair: form.pair.trim().toUpperCase(),
      direction: form.direction,
      entry: Number(form.entry),
      exit_price:
        form.exit_price.trim() === ""
          ? null
          : Number(form.exit_price),
      stop_loss: Number(form.stop_loss),
      take_profit: Number(form.take_profit),
      lot_size:
        form.lot_size.trim() === ""
          ? null
          : Number(form.lot_size),
      profit:
        form.profit.trim() === ""
          ? null
          : Number(form.profit),
      commission: 0,
      swap: 0,
      strategy: form.strategy.trim() || null,
      emotion: form.emotion.trim() || null,
      notes: form.notes.trim() || null,
      imported: false,
    }

    if (editingTrade) {
      await updateMutation.mutateAsync({
        id: editingTrade.id,
        payload,
      })
    } else {
      await createMutation.mutateAsync(payload)
    }
  }

  async function openTradeReview(trade: Trade) {
    setReview({
      trade,
      loading: true,
    })

    try {
      const data = await fetchTradeReview(trade.id)

      setReview({
        trade,
        data,
      })
    } catch {
      setReview({
        trade,
        error: "Unable to generate this trade review.",
      })
    }
  }

  return (
    <div className="space-y-6">
      <section className="premium-card grid-surface rounded-[2rem] p-8">
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-blue-300">
              Trade journal
            </p>

            <h2 className="mt-4 text-4xl font-semibold">
              Every trade becomes intelligence.
            </h2>

            <p className="mt-3 text-slate-400">
              Record, review and improve every execution.
            </p>
          </div>

          <button
            onClick={openNewTrade}
            className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-3 font-semibold text-white"
          >
            <Plus className="size-4" />
            Add trade
          </button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">Total trades</p>
          <p className="mt-2 text-3xl font-semibold">{trades.length}</p>
        </div>

        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">Winning trades</p>
          <p className="mt-2 text-3xl font-semibold text-emerald-300">
            {trades.filter((trade) => (trade.profit ?? 0) > 0).length}
          </p>
        </div>

        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">Losing trades</p>
          <p className="mt-2 text-3xl font-semibold text-red-300">
            {trades.filter((trade) => (trade.profit ?? 0) < 0).length}
          </p>
        </div>
      </section>

      <div className="premium-card flex items-center gap-3 rounded-3xl px-4">
        <Search className="size-4 text-slate-500" />

        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search pair, strategy, broker or ticket..."
          className="w-full bg-transparent py-3 outline-none"
        />
      </div>

      {tradesQuery.isLoading ? (
        <div className="grid min-h-[320px] place-items-center">
          <div className="size-10 animate-spin rounded-full border-2 border-blue-400/20 border-t-blue-400" />
        </div>
      ) : tradesQuery.isError ? (
        <div className="premium-card rounded-[2rem] p-8 text-red-300">
          Unable to load trades.
        </div>
      ) : (
        <div className="premium-card overflow-x-auto rounded-[2rem]">
          <table className="w-full min-w-[950px] text-left">
            <thead className="border-b border-white/10 text-xs uppercase tracking-[0.15em] text-slate-500">
              <tr>
                <th className="px-5 py-4">Market</th>
                <th className="px-5 py-4">Direction</th>
                <th className="px-5 py-4">Entry</th>
                <th className="px-5 py-4">Exit</th>
                <th className="px-5 py-4">Size</th>
                <th className="px-5 py-4">Profit</th>
                <th className="px-5 py-4">Strategy</th>
                <th className="px-5 py-4">Actions</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-white/[0.06]">
              {filteredTrades.map((trade) => (
                <tr
                  key={trade.id}
                  className="transition hover:bg-white/[0.02]"
                >
                  <td className="px-5 py-4">
                    <p className="font-semibold">{trade.pair}</p>
                    <p className="text-xs text-slate-500">
                      {trade.broker || "Manual"} ·{" "}
                      {trade.ticket || `#${trade.id}`}
                    </p>
                  </td>

                  <td
                    className={[
                      "px-5 py-4 font-semibold",
                      trade.direction === "BUY"
                        ? "text-emerald-300"
                        : "text-red-300",
                    ].join(" ")}
                  >
                    {trade.direction}
                  </td>

                  <td className="px-5 py-4">{trade.entry}</td>
                  <td className="px-5 py-4">
                    {trade.exit_price ?? "—"}
                  </td>
                  <td className="px-5 py-4">
                    {trade.lot_size ?? "—"}
                  </td>
                  <td
                    className={[
                      "px-5 py-4 font-semibold",
                      (trade.profit ?? 0) >= 0
                        ? "text-emerald-300"
                        : "text-red-300",
                    ].join(" ")}
                  >
                    {trade.profit ?? 0}
                  </td>
                  <td className="px-5 py-4">
                    {trade.strategy || "Unspecified"}
                  </td>

                  <td className="px-5 py-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => openTradeReview(trade)}
                        className="grid size-9 place-items-center rounded-xl bg-blue-400/10 text-blue-300"
                        title="AI review"
                      >
                        <BrainCircuit className="size-4" />
                      </button>

                      <button
                        onClick={() => openEditTrade(trade)}
                        className="grid size-9 place-items-center rounded-xl bg-white/[0.04]"
                        title="Edit"
                      >
                        <Pencil className="size-4" />
                      </button>

                      <button
                        onClick={() => {
                          if (window.confirm("Delete this trade?")) {
                            deleteMutation.mutate(trade.id)
                          }
                        }}
                        className="grid size-9 place-items-center rounded-xl bg-red-400/10 text-red-300"
                        title="Delete"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {!filteredTrades.length ? (
            <div className="p-10 text-center text-slate-500">
              No trades found.
            </div>
          ) : null}
        </div>
      )}

      {formOpen ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="premium-card max-h-[92vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] p-7">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
                  {editingTrade ? "Edit trade" : "New trade"}
                </p>

                <h3 className="mt-2 text-2xl font-semibold">
                  {editingTrade
                    ? editingTrade.pair
                    : "Add journal entry"}
                </h3>
              </div>

              <button onClick={() => setFormOpen(false)}>
                <X />
              </button>
            </div>

            <form
              onSubmit={submitTrade}
              className="mt-6 space-y-4"
            >
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <input
                  placeholder="Pair"
                  required
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={form.pair}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      pair: event.target.value,
                    })
                  }
                />

                <select
                  className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
                  value={form.direction}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      direction: event.target.value as "BUY" | "SELL",
                    })
                  }
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>

                <input
                  placeholder="Broker"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={form.broker}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      broker: event.target.value,
                    })
                  }
                />

                <input
                  placeholder="Ticket"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={form.ticket}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      ticket: event.target.value,
                    })
                  }
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                {[
                  ["entry", "Entry"],
                  ["exit_price", "Exit"],
                  ["stop_loss", "Stop loss"],
                  ["take_profit", "Take profit"],
                  ["lot_size", "Lot size"],
                ].map(([key, label]) => (
                  <input
                    key={key}
                    type="number"
                    step="any"
                    required={
                      key === "entry" ||
                      key === "stop_loss" ||
                      key === "take_profit"
                    }
                    placeholder={label}
                    className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                    value={form[key as keyof typeof form]}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        [key]: event.target.value,
                      })
                    }
                  />
                ))}
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <input
                  type="number"
                  step="any"
                  placeholder="Profit"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={form.profit}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      profit: event.target.value,
                    })
                  }
                />

                <input
                  placeholder="Strategy"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={form.strategy}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      strategy: event.target.value,
                    })
                  }
                />

                <input
                  placeholder="Emotion"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={form.emotion}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      emotion: event.target.value,
                    })
                  }
                />
              </div>

              <textarea
                rows={4}
                placeholder="Notes"
                className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                value={form.notes}
                onChange={(event) =>
                  setForm({
                    ...form,
                    notes: event.target.value,
                  })
                }
              />

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setFormOpen(false)}
                  className="rounded-2xl border border-white/10 px-5 py-3"
                >
                  Cancel
                </button>

                <button
                  disabled={
                    createMutation.isPending ||
                    updateMutation.isPending
                  }
                  className="rounded-2xl bg-blue-500 px-5 py-3 font-semibold"
                >
                  {createMutation.isPending ||
                  updateMutation.isPending
                    ? "Saving..."
                    : "Save trade"}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}

      {review ? (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60">
          <aside className="h-full w-full max-w-xl overflow-y-auto border-l border-white/10 bg-[#090f1c] p-8">
            <div className="flex items-start justify-between">
              <h3 className="text-2xl font-semibold">
                AI review · {review.trade.pair}
              </h3>

              <button onClick={() => setReview(null)}>
                <X />
              </button>
            </div>

            {review.loading ? (
              <p className="mt-10 text-slate-400">
                Reviewing trade...
              </p>
            ) : review.error ? (
              <p className="mt-10 text-red-300">
                {review.error}
              </p>
            ) : review.data ? (
              <div className="mt-8 space-y-5">
                <div className="premium-card rounded-3xl p-5">
                  <p className="text-4xl font-semibold text-blue-300">
                    {review.data.trade_score}
                  </p>

                  <p className="mt-2">
                    {review.data.summary}
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-emerald-300">
                    Strengths
                  </h4>

                  {review.data.strengths.map((item) => (
                    <p
                      key={item}
                      className="mt-2 rounded-2xl bg-emerald-400/[0.05] p-3"
                    >
                      {item}
                    </p>
                  ))}
                </div>

                <div>
                  <h4 className="font-semibold text-red-300">
                    Mistakes
                  </h4>

                  {review.data.mistakes.map((item) => (
                    <p
                      key={item}
                      className="mt-2 rounded-2xl bg-red-400/[0.05] p-3"
                    >
                      {item}
                    </p>
                  ))}
                </div>

                <div className="premium-card rounded-3xl p-5">
                  <strong>Lesson</strong>
                  <p className="mt-2 text-slate-300">
                    {review.data.lesson}
                  </p>
                </div>

                <div className="rounded-3xl bg-blue-400/[0.06] p-5">
                  <strong>Next mission</strong>
                  <p className="mt-2">
                    {review.data.next_mission}
                  </p>
                </div>
              </div>
            ) : null}
          </aside>
        </div>
      ) : null}
    </div>
  )
}
