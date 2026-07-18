import { Activity, BrainCircuit, Percent, TrendingUp } from "lucide-react"
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { useQuery } from "@tanstack/react-query"
import StatCard from "@/components/dashboard/StatCard"
import { fetchDashboard } from "@/api/dashboard"

function formatMoney(value: number | undefined) {
  return new Intl.NumberFormat("en-ZA", { style: "currency", currency: "ZAR", maximumFractionDigits: 2 }).format(value || 0)
}

export default function DashboardPage() {
  const { data, isLoading, isError, error } = useQuery({ queryKey: ["dashboard"], queryFn: fetchDashboard })
  if (isLoading) return <div className="grid min-h-[60vh] place-items-center"><div className="text-center"><div className="mx-auto size-10 animate-spin rounded-full border-2 border-blue-400/20 border-t-blue-400"/><p className="mt-4 text-sm text-slate-400">Loading your trading intelligence...</p></div></div>
  if (isError) return <section className="premium-card rounded-[2rem] p-8"><p className="text-sm text-red-300">Unable to load dashboard data.</p><p className="mt-2 text-xs text-slate-500">{error instanceof Error ? error.message : "Unknown error"}</p></section>

  const summary = data?.summary || {}
  const intelligence = data?.intelligence || {}
  const headline = intelligence.headline || {}
  const mission = intelligence.mission || {}
  const scorecard = intelligence.scorecard || {}
  const equityCurve = data?.equity_curve || []

  return <div className="space-y-6">
    <section className="premium-card grid-surface overflow-hidden rounded-[2rem] p-6 sm:p-8">
      <p className="text-xs uppercase tracking-[0.25em] text-blue-300">AI-powered performance brief</p>
      <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">{headline.title || "Your trading intelligence is ready."}</h2>
      <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-400">{headline.message || "TradePilot AI is analyzing your trading performance."}</p>
    </section>
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Net Profit" value={formatMoney(summary.net_profit)} helper={`${summary.total_trades || 0} total trades`} icon={TrendingUp}/>
      <StatCard label="Win Rate" value={`${summary.win_rate || 0}%`} helper="Closed-trade performance" icon={Percent}/>
      <StatCard label="Profit Factor" value={`${summary.profit_factor || 0}`} helper="Gross profit vs gross loss" icon={Activity}/>
      <StatCard label="Trader DNA" value={`${scorecard.overall || 0}/100`} helper={`Consistency ${scorecard.consistency || 0}/100`} icon={BrainCircuit}/>
    </section>
    <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
      <div className="premium-card rounded-[2rem] p-5 sm:p-6"><p className="text-sm text-slate-500">Performance</p><h3 className="mt-1 text-xl font-semibold">Equity curve</h3><div className="mt-6 h-80">{equityCurve.length ? <ResponsiveContainer width="100%" height="100%"><AreaChart data={equityCurve}><defs><linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#4f7cff" stopOpacity={0.45}/><stop offset="100%" stopColor="#4f7cff" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="rgba(148,163,184,.08)" vertical={false}/><XAxis dataKey="date" stroke="#64748b" tickLine={false} axisLine={false}/><YAxis stroke="#64748b" tickLine={false} axisLine={false}/><Tooltip contentStyle={{background:"#0b1120",border:"1px solid rgba(148,163,184,.15)",borderRadius:16}}/><Area type="monotone" dataKey="balance" stroke="#6d8dff" fill="url(#equityFill)" strokeWidth={3}/></AreaChart></ResponsiveContainer> : <div className="grid h-full place-items-center rounded-2xl border border-dashed border-white/10"><p className="text-sm text-slate-400">No equity data yet</p></div>}</div></div>
      <div className="premium-card rounded-[2rem] p-6"><p className="text-sm text-slate-500">Today’s mission</p><h3 className="mt-2 text-2xl font-semibold">{mission.today || "Execute only trades that match your plan."}</h3><p className="mt-3 text-sm leading-6 text-slate-400">{mission.this_week || "Maintain consistent execution across every session."}</p></div>
    </section>
  </div>
}
