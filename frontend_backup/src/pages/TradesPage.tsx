import { useMemo, useState, type FormEvent } from "react"
import { BrainCircuit, Pencil, Plus, RefreshCw, Search, Trash2, X } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createTrade, deleteTrade, fetchTradeReview, fetchTrades, updateTrade } from "@/api/trades"
import type { Trade, TradePayload, TradeReview } from "@/types/trade"

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
  opened_at: "",
  closed_at: "",
}

type FormState = typeof emptyForm

function money(value?: number | null) {
  return new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: "ZAR",
    maximumFractionDigits: 2,
  }).format(value || 0)
}

function localDate(value?: string | null) {
  if (!value) return ""
  const d = new Date(value)
  return new Date(d.getTime() - d.getTimezoneOffset() * 60_000).toISOString().slice(0, 16)
}

export default function TradesPage() {
  const client = useQueryClient()
  const [search, setSearch] = useState("")
  const [direction, setDirection] = useState("")
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Trade | null>(null)
  const [deleting, setDeleting] = useState<Trade | null>(null)
  const [reviewing, setReviewing] = useState<Trade | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm)
  const [formError, setFormError] = useState("")

  const tradesQuery = useQuery({ queryKey: ["trades"], queryFn: fetchTrades })
  const reviewQuery = useQuery({
    queryKey: ["trade-review", reviewing?.id],
    queryFn: () => fetchTradeReview(reviewing!.id),
    enabled: Boolean(reviewing),
  })

  const refresh = async () => {
    await client.invalidateQueries({ queryKey: ["trades"] })
    await client.invalidateQueries({ queryKey: ["dashboard"] })
  }

  const createMutation = useMutation({
    mutationFn: createTrade,
    onSuccess: async () => { await refresh(); closeForm() },
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<TradePayload> }) => updateTrade(id, payload),
    onSuccess: async () => { await refresh(); closeForm() },
  })
  const deleteMutation = useMutation({
    mutationFn: deleteTrade,
    onSuccess: async () => { await refresh(); setDeleting(null) },
  })

  const trades = tradesQuery.data?.trades || []
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return trades.filter((t) => {
      const text = [t.pair, t.strategy, t.broker, t.ticket, t.notes].filter(Boolean).join(" ").toLowerCase()
      return (!q || text.includes(q)) && (!direction || t.direction === direction)
    })
  }, [trades, search, direction])

  function closeForm() {
    setModalOpen(false)
    setEditing(null)
    setForm(emptyForm)
    setFormError("")
  }

  function openNew() {
    setEditing(null)
    setForm(emptyForm)
    setModalOpen(true)
  }

  function openEdit(trade: Trade) {
    setEditing(trade)
    setForm({
      broker: trade.broker || "",
      ticket: trade.ticket || "",
      pair: trade.pair,
      direction: trade.direction,
      entry: String(trade.entry ?? ""),
      exit_price: String(trade.exit_price ?? ""),
      stop_loss: String(trade.stop_loss ?? ""),
      take_profit: String(trade.take_profit ?? ""),
      lot_size: String(trade.lot_size ?? ""),
      profit: String(trade.profit ?? ""),
      strategy: trade.strategy || "",
      emotion: trade.emotion || "",
      notes: trade.notes || "",
      opened_at: localDate(trade.opened_at),
      closed_at: localDate(trade.closed_at),
    })
    setModalOpen(true)
  }

  function num(value: string) { return value === "" ? null : Number(value) }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setFormError("")
    if (!form.pair || !form.entry || !form.stop_loss || !form.take_profit) {
      setFormError("Pair, entry, stop loss and take profit are required.")
      return
    }

    const payload: TradePayload = {
      broker: form.broker || null,
      ticket: form.ticket || null,
      pair: form.pair.toUpperCase(),
      direction: form.direction,
      entry: Number(form.entry),
      exit_price: num(form.exit_price),
      stop_loss: Number(form.stop_loss),
      take_profit: Number(form.take_profit),
      lot_size: num(form.lot_size),
      profit: num(form.profit),
      commission: 0,
      swap: 0,
      strategy: form.strategy || null,
      emotion: form.emotion || null,
      notes: form.notes || null,
      opened_at: form.opened_at ? new Date(form.opened_at).toISOString() : null,
      closed_at: form.closed_at ? new Date(form.closed_at).toISOString() : null,
      imported: false,
    }

    try {
      if (editing) await updateMutation.mutateAsync({ id: editing.id, payload })
      else await createMutation.mutateAsync(payload)
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Unable to save trade.")
    }
  }

  const saving = createMutation.isPending || updateMutation.isPending
  const inputClass = "w-full rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-3 text-sm outline-none focus:border-blue-400/40"

  return (
    <div className="space-y-6">
      <section className="premium-card grid-surface rounded-[2rem] p-6 sm:p-8">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-blue-300">Trade journal</p>
            <h2 className="mt-4 text-3xl font-semibold sm:text-4xl">Every trade becomes intelligence.</h2>
            <p className="mt-3 text-sm text-slate-400">Record, filter, edit and review every execution.</p>
          </div>
          <button onClick={openNew} className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-3 text-sm font-semibold">
            <Plus className="size-4" /> Add trade
          </button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="premium-card rounded-3xl p-5"><p className="text-sm text-slate-500">Total trades</p><p className="mt-2 text-3xl font-semibold">{trades.length}</p></div>
        <div className="premium-card rounded-3xl p-5"><p className="text-sm text-slate-500">Winners</p><p className="mt-2 text-3xl font-semibold text-emerald-300">{trades.filter(t => (t.profit || 0) > 0).length}</p></div>
        <div className="premium-card rounded-3xl p-5"><p className="text-sm text-slate-500">Losers</p><p className="mt-2 text-3xl font-semibold text-red-300">{trades.filter(t => (t.profit || 0) < 0).length}</p></div>
      </section>

      <section className="premium-card rounded-3xl p-4">
        <div className="grid gap-3 md:grid-cols-[1fr_180px]">
          <label className="flex items-center gap-3 rounded-2xl border border-white/10 px-4"><Search className="size-4 text-slate-500" /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search trades..." className="w-full bg-transparent py-3 text-sm outline-none" /></label>
          <select value={direction} onChange={e => setDirection(e.target.value)} className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm"><option value="" className="bg-[#0b1120]">All directions</option><option value="BUY" className="bg-[#0b1120]">BUY</option><option value="SELL" className="bg-[#0b1120]">SELL</option></select>
        </div>
      </section>

      {tradesQuery.isLoading ? (
        <div className="grid min-h-[40vh] place-items-center"><div className="size-10 animate-spin rounded-full border-2 border-blue-400/20 border-t-blue-400" /></div>
      ) : tradesQuery.isError ? (
        <div className="premium-card rounded-[2rem] p-8"><p className="text-red-300">Unable to load trades.</p><button onClick={() => tradesQuery.refetch()} className="mt-4 flex items-center gap-2"><RefreshCw className="size-4" />Retry</button></div>
      ) : (
        <div className="premium-card overflow-hidden rounded-[2rem]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[950px] text-left">
              <thead className="border-b border-white/10 text-xs uppercase tracking-[0.15em] text-slate-500"><tr><th className="px-6 py-4">Market</th><th className="px-4 py-4">Side</th><th className="px-4 py-4">Entry</th><th className="px-4 py-4">Exit</th><th className="px-4 py-4">Profit</th><th className="px-4 py-4">Strategy</th><th className="px-6 py-4 text-right">Actions</th></tr></thead>
              <tbody className="divide-y divide-white/[0.06]">
                {filtered.map(trade => (
                  <tr key={trade.id} className="hover:bg-white/[0.025]">
                    <td className="px-6 py-5"><p className="font-semibold">{trade.pair}</p><p className="mt-1 text-xs text-slate-500">{trade.broker || "Manual"} · {trade.ticket || `#${trade.id}`}</p></td>
                    <td className="px-4 py-5"><span className={trade.direction === "BUY" ? "rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300" : "rounded-full bg-red-400/10 px-3 py-1 text-xs text-red-300"}>{trade.direction}</span></td>
                    <td className="px-4 py-5 text-sm text-slate-300">{trade.entry}</td>
                    <td className="px-4 py-5 text-sm text-slate-300">{trade.exit_price ?? "—"}</td>
                    <td className={(trade.profit || 0) >= 0 ? "px-4 py-5 font-semibold text-emerald-300" : "px-4 py-5 font-semibold text-red-300"}>{money(trade.profit)}</td>
                    <td className="px-4 py-5 text-sm text-slate-300">{trade.strategy || "Unspecified"}</td>
                    <td className="px-6 py-5"><div className="flex justify-end gap-2"><button onClick={() => setReviewing(trade)} className="grid size-9 place-items-center rounded-xl bg-blue-400/10 text-blue-300"><BrainCircuit className="size-4" /></button><button onClick={() => openEdit(trade)} className="grid size-9 place-items-center rounded-xl bg-white/[0.05]"><Pencil className="size-4" /></button><button onClick={() => setDeleting(trade)} className="grid size-9 place-items-center rounded-xl bg-red-400/10 text-red-300"><Trash2 className="size-4" /></button></div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="premium-card max-h-[92vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] p-6 sm:p-8">
            <div className="flex justify-between"><div><p className="text-xs uppercase tracking-[0.22em] text-blue-300">{editing ? "Edit trade" : "New trade"}</p><h3 className="mt-3 text-2xl font-semibold">{editing ? `${editing.pair} trade` : "Add journal entry"}</h3></div><button onClick={closeForm} className="grid size-10 place-items-center rounded-2xl border border-white/10"><X className="size-5" /></button></div>
            <form onSubmit={submit} className="mt-8 space-y-5">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <label><span className="mb-2 block text-sm text-slate-400">Pair</span><input className={inputClass} value={form.pair} onChange={e => setForm({...form, pair:e.target.value})} /></label>
                <label><span className="mb-2 block text-sm text-slate-400">Direction</span><select className={inputClass} value={form.direction} onChange={e => setForm({...form, direction:e.target.value as "BUY"|"SELL"})}><option value="BUY">BUY</option><option value="SELL">SELL</option></select></label>
                <label><span className="mb-2 block text-sm text-slate-400">Broker</span><input className={inputClass} value={form.broker} onChange={e => setForm({...form, broker:e.target.value})} /></label>
                <label><span className="mb-2 block text-sm text-slate-400">Ticket</span><input className={inputClass} value={form.ticket} onChange={e => setForm({...form, ticket:e.target.value})} /></label>
              </div>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                {([['entry','Entry'],['exit_price','Exit'],['stop_loss','Stop loss'],['take_profit','Take profit'],['lot_size','Lot size']] as const).map(([key,label]) => <label key={key}><span className="mb-2 block text-sm text-slate-400">{label}</span><input type="number" step="any" className={inputClass} value={form[key]} onChange={e => setForm({...form,[key]:e.target.value})} /></label>)}
              </div>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <label><span className="mb-2 block text-sm text-slate-400">Profit</span><input type="number" step="any" className={inputClass} value={form.profit} onChange={e => setForm({...form,profit:e.target.value})} /></label>
                <label><span className="mb-2 block text-sm text-slate-400">Strategy</span><input className={inputClass} value={form.strategy} onChange={e => setForm({...form,strategy:e.target.value})} /></label>
                <label><span className="mb-2 block text-sm text-slate-400">Emotion</span><input className={inputClass} value={form.emotion} onChange={e => setForm({...form,emotion:e.target.value})} /></label>
                <label><span className="mb-2 block text-sm text-slate-400">Opened</span><input type="datetime-local" className={inputClass} value={form.opened_at} onChange={e => setForm({...form,opened_at:e.target.value})} /></label>
              </div>
              <div className="grid gap-4 md:grid-cols-[1fr_240px]"><label><span className="mb-2 block text-sm text-slate-400">Notes</span><textarea rows={4} className={inputClass} value={form.notes} onChange={e => setForm({...form,notes:e.target.value})} /></label><label><span className="mb-2 block text-sm text-slate-400">Closed</span><input type="datetime-local" className={inputClass} value={form.closed_at} onChange={e => setForm({...form,closed_at:e.target.value})} /></label></div>
              {formError && <div className="rounded-2xl border border-red-400/20 bg-red-400/[0.07] px-4 py-3 text-sm text-red-300">{formError}</div>}
              <div className="flex justify-end gap-3"><button type="button" onClick={closeForm} className="rounded-2xl border border-white/10 px-5 py-3">Cancel</button><button disabled={saving} className="rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-3 font-semibold disabled:opacity-60">{saving ? "Saving..." : editing ? "Save changes" : "Add trade"}</button></div>
            </form>
          </div>
        </div>
      )}

      {deleting && <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><div className="premium-card w-full max-w-md rounded-[2rem] p-7"><h3 className="text-2xl font-semibold">Delete this trade?</h3><p className="mt-3 text-sm text-slate-400">{deleting.pair} #{deleting.id} will be permanently removed.</p><div className="mt-7 flex justify-end gap-3"><button onClick={() => setDeleting(null)} className="rounded-2xl border border-white/10 px-5 py-3">Cancel</button><button onClick={() => deleteMutation.mutate(deleting.id)} className="rounded-2xl bg-red-500 px-5 py-3 font-semibold">{deleteMutation.isPending ? "Deleting..." : "Delete"}</button></div></div></div>}

      {reviewing && <ReviewPanel trade={reviewing} review={reviewQuery.data} loading={reviewQuery.isLoading} onClose={() => setReviewing(null)} />}
    </div>
  )
}

function ReviewPanel({ trade, review, loading, onClose }: { trade: Trade; review?: TradeReview; loading: boolean; onClose: () => void }) {
  return <div className="fixed inset-0 z-50 flex justify-end bg-black/60"><aside className="h-full w-full max-w-xl overflow-y-auto border-l border-white/10 bg-[#090f1c] p-6 sm:p-8"><div className="flex justify-between"><div><p className="text-xs uppercase tracking-[0.22em] text-blue-300">AI trade review</p><h3 className="mt-3 text-2xl font-semibold">{trade.pair} · {trade.direction}</h3></div><button onClick={onClose}><X className="size-5" /></button></div>{loading ? <div className="grid min-h-[50vh] place-items-center"><div className="size-10 animate-spin rounded-full border-2 border-blue-400/20 border-t-blue-400" /></div> : review ? <div className="mt-8 space-y-6"><div className="premium-card rounded-3xl p-6"><p className="text-sm text-slate-500">Trade score</p><p className="mt-2 text-4xl font-semibold text-blue-300">{review.trade_score}</p><p className="mt-3 text-sm text-slate-300">{review.summary}</p></div><section><h4 className="font-semibold text-emerald-300">Strengths</h4><div className="mt-3 space-y-2">{review.strengths.map(x => <div key={x} className="rounded-2xl bg-emerald-400/[0.05] px-4 py-3 text-sm">{x}</div>)}</div></section><section><h4 className="font-semibold text-red-300">Mistakes</h4><div className="mt-3 space-y-2">{review.mistakes.map(x => <div key={x} className="rounded-2xl bg-red-400/[0.05] px-4 py-3 text-sm">{x}</div>)}</div></section><div className="premium-card rounded-3xl p-5"><p className="text-xs uppercase tracking-[0.2em] text-amber-300">Lesson</p><p className="mt-3 text-sm">{review.lesson}</p></div><div className="rounded-3xl border border-blue-400/15 bg-blue-400/[0.05] p-5"><p className="text-xs uppercase tracking-[0.2em] text-blue-300">Next mission</p><p className="mt-3 font-semibold">{review.next_mission}</p></div></div> : <p className="mt-8 text-red-300">Unable to load review.</p>}</aside></div>
}
