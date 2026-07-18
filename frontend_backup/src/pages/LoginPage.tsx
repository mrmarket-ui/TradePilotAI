import { useState, type FormEvent } from "react"
import axios from "axios"
import { ArrowRight, ChartNoAxesCombined, Eye, EyeOff, LockKeyhole, Mail } from "lucide-react"
import { Navigate, useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "@/providers/AuthProvider"

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isAuthenticated } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [show, setShow] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const destination = (location.state as { from?: string } | null)?.from || "/dashboard"

  if (isAuthenticated) return <Navigate to={destination} replace />

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setBusy(true)
    try { await login({ email: email.trim(), password }); navigate(destination, { replace: true }) }
    catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        const detail = requestError.response?.data?.detail
        setError(typeof detail === "string" ? detail : "Invalid email or password.")
      } else setError(requestError instanceof Error ? requestError.message : "Unable to sign in.")
    } finally { setBusy(false) }
  }

  return <div className="relative min-h-screen overflow-hidden bg-[#060912]">
    <div className="absolute inset-0 grid-surface opacity-40" />
    <div className="relative mx-auto grid min-h-screen max-w-7xl items-center gap-16 px-5 py-10 lg:grid-cols-[1.15fr_0.85fr] lg:px-10">
      <section className="hidden lg:block">
        <div className="flex items-center gap-3"><div className="grid size-12 place-items-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-700"><ChartNoAxesCombined className="size-7" /></div><div><p className="text-xl font-semibold">TradePilot AI</p><p className="text-xs uppercase tracking-[0.25em] text-slate-500">Trading intelligence</p></div></div>
        <h1 className="mt-14 max-w-2xl text-5xl font-semibold leading-[1.08] tracking-[-0.04em]">Understand your trading.<span className="gold-text"> Master your execution.</span></h1>
        <p className="mt-6 max-w-xl text-base leading-7 text-slate-400">One premium workspace for risk analytics, psychology, Trader DNA, AI coaching and professional performance reports.</p>
      </section>
      <section className="premium-card mx-auto w-full max-w-md rounded-[2rem] p-6 sm:p-8">
        <p className="text-xs uppercase tracking-[0.25em] text-blue-300">Secure access</p><h2 className="mt-4 text-3xl font-semibold">Welcome back</h2><p className="mt-2 text-sm text-slate-400">Sign in to your trading intelligence workspace.</p>
        <form className="mt-8 space-y-5" onSubmit={submit}>
          <label className="block"><span className="mb-2 block text-sm text-slate-300">Email address</span><div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.035] px-4"><Mail className="size-4 text-slate-500"/><input type="email" required value={email} onChange={e=>setEmail(e.target.value)} className="w-full bg-transparent py-3.5 text-sm outline-none"/></div></label>
          <label className="block"><span className="mb-2 block text-sm text-slate-300">Password</span><div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.035] px-4"><LockKeyhole className="size-4 text-slate-500"/><input type={show?"text":"password"} required value={password} onChange={e=>setPassword(e.target.value)} className="w-full bg-transparent py-3.5 text-sm outline-none"/><button type="button" onClick={()=>setShow(v=>!v)}>{show?<EyeOff className="size-4"/>:<Eye className="size-4"/>}</button></div></label>
          {error ? <div className="rounded-2xl border border-red-400/20 bg-red-400/[0.07] px-4 py-3 text-sm text-red-300">{error}</div> : null}
          <button type="submit" disabled={busy} className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-3.5 text-sm font-semibold text-white">{busy?"Signing in...":"Enter workspace"}{!busy?<ArrowRight className="size-4"/>:null}</button>
        </form>
      </section>
    </div>
  </div>
}
