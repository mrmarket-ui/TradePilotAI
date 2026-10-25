import {useMemo,useState,type FormEvent} from "react"
import {Link,Navigate,useLocation,useNavigate} from "react-router-dom"
import {useMutation,useQuery,useQueryClient} from "@tanstack/react-query"
import {Area,AreaChart,CartesianGrid,ResponsiveContainer,Tooltip,XAxis,YAxis} from "recharts"
import {Plus,Search,Pencil,Trash2,BrainCircuit,Upload,ExternalLink,Check} from "lucide-react"
import {useAuth} from "@/Auth"
import {useTranslation} from "react-i18next"
import {updatePreferences} from "@/api/profile/preferences"
import {supportedCurrencies} from "@/utils/currency"
import {dashboard,analysis,trades,addTrade,editTrade,removeTrade,reviewTrade,weekly,monthly,coach,createPayPalSubscription,mySubscription,cancelSubscription,registerUser} from "@/api"
import type {Trade,TradePayload} from "@/types"
export function Login(){
  const {
    login,
    isAuthenticated,
  }=useAuth()

  const nav=useNavigate()
  const loc=useLocation()

  const [email,setEmail]=useState("")
  const [password,setPassword]=useState("")
  const [error,setError]=useState("")
  const [busy,setBusy]=useState(false)

  const destination=
    (loc.state as any)?.from||
    "/dashboard"

  if(isAuthenticated){
    return(
      <Navigate
        to={destination}
        replace
      />
    )
  }

  async function sub(e:FormEvent){
    e.preventDefault()

    if(busy){
      return
    }

    setBusy(true)
    setError("")

    try{
      await login({
        email,
        password,
      })

      nav(
        destination,
        {
          replace:true,
        },
      )
    }catch{
      setError(
        "Invalid email or password.",
      )
    }finally{
      setBusy(false)
    }
  }

  return(
    <div className="auth-shell">
      <div className="auth-orb auth-orb-one"/>
      <div className="auth-orb auth-orb-two"/>

      <div className="auth-grid mx-auto grid w-full max-w-7xl items-center gap-10 px-4 py-8 sm:px-6 lg:min-h-screen lg:grid-cols-[1.08fr_.92fr] lg:px-10">
        <section className="auth-showcase hidden lg:block">
          <div className="auth-brand-row">
            <div className="auth-brand-mark">
              TP
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-[.32em] text-blue-300">
                TradePilot AI
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Trading intelligence workspace
              </p>
            </div>
          </div>

          <div className="mt-12">
            <div className="auth-pill">
              AI-powered trading intelligence
            </div>

            <h1 className="mt-6 max-w-3xl text-5xl font-semibold leading-[1.06] xl:text-6xl">
              Understand your trading.
              <span className="auth-gradient-text block">
                Improve your process.
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">
              TradePilot AI turns your journal, performance and trading behaviour
              into structured intelligence designed to support better decision-making.
            </p>
          </div>

          <div className="mt-10 grid max-w-2xl gap-4 sm:grid-cols-2">
            {[
              [
                "Trading Journal",
                "Capture every setup, result and lesson.",
              ],
              [
                "Performance Analytics",
                "See the patterns behind your results.",
              ],
              [
                "AI Coach",
                "Review psychology, risk and consistency.",
              ],
              [
                "Strategy Intelligence",
                "Build rules around how you actually trade.",
              ],
            ].map(([title,description])=>(
              <div
                key={title}
                className="auth-feature-card"
              >
                <div className="auth-check">
                  <Check className="size-4"/>
                </div>

                <div>
                  <p className="text-sm font-semibold text-slate-200">
                    {title}
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    {description}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="auth-trust-strip mt-8 max-w-2xl">
            <div>
              <p className="text-xs uppercase tracking-[.2em] text-slate-500">
                Built for
              </p>
              <p className="mt-1 text-sm font-medium">
                Process ? Discipline ? Review
              </p>
            </div>

            <div className="h-8 w-px bg-white/[.08]"/>

            <div>
              <p className="text-xs uppercase tracking-[.2em] text-slate-500">
                Access
              </p>
              <p className="mt-1 text-sm font-medium">
                Free ? Pro ? Premium
              </p>
            </div>
          </div>
        </section>

        <section className="mx-auto w-full max-w-md">
          <div className="auth-card">
            <div className="lg:hidden">
              <div className="auth-brand-row">
                <div className="auth-brand-mark">
                  TP
                </div>

                <div>
                  <p className="text-xs font-semibold uppercase tracking-[.28em] text-blue-300">
                    TradePilot AI
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Trading intelligence workspace
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8 lg:mt-0">
              <div className="auth-pill">
                Secure workspace
              </div>

              <h2 className="mt-5 text-3xl font-semibold">
                Welcome back
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Sign in to continue to your TradePilot AI workspace.
              </p>
            </div>

            <form
              onSubmit={sub}
              className="mt-8"
            >
              <label className="auth-label">
                Email address
              </label>

              <input
                className="auth-input"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                value={email}
                onChange={e=>setEmail(e.target.value)}
                required
              />

              <label className="auth-label mt-5">
                Password
              </label>

              <input
                className="auth-input"
                type="password"
                placeholder="Enter your password"
                autoComplete="current-password"
                value={password}
                onChange={e=>setPassword(e.target.value)}
                required
              />

              {error&&(
                <div className="mt-4 rounded-2xl border border-red-400/10 bg-red-400/10 p-3 text-sm text-red-300">
                  {error}
                </div>
              )}

              <button
                disabled={busy}
                className="auth-primary-button"
              >
                {busy
                  ?"Signing in..."
                  :"Enter workspace"}
              </button>
            </form>

            <div className="mt-7 border-t border-white/[.07] pt-6 text-center">
              <p className="text-sm text-slate-500">
                New to TradePilot AI?
              </p>

              <Link
                to="/register"
                className="mt-3 inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-blue-300 transition hover:bg-blue-400/10 hover:text-blue-200"
              >
                Create a free account
              </Link>
            </div>

            <p className="mt-5 text-center text-[11px] leading-5 text-slate-600">
              Analytical and educational tools only. Trading involves financial risk.
            </p>
          </div>
        </section>
      </div>
    </div>
  )
}


export function Register(){
  const {
    login,
    isAuthenticated,
  }=useAuth()

  const nav=useNavigate()

  const [email,setEmail]=useState("")
  const [password,setPassword]=useState("")
  const [confirmPassword,setConfirmPassword]=useState("")
  const [acceptedTerms,setAcceptedTerms]=useState(false)
  const [error,setError]=useState("")
  const [busy,setBusy]=useState(false)

  if(isAuthenticated){
    return(
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  async function sub(e:FormEvent){
    e.preventDefault()

    if(busy){
      return
    }

    setError("")

    const cleanEmail=
      email.trim().toLowerCase()

    if(password.length<8){
      setError(
        "Use at least 8 characters for your password.",
      )
      return
    }

    if(password!==confirmPassword){
      setError(
        "The passwords do not match.",
      )
      return
    }

    if(!acceptedTerms){
      setError(
        "Please accept the Terms & Conditions to create your account.",
      )
      return
    }

    setBusy(true)

    try{
      await registerUser(
        cleanEmail,
        password,
      )

      await login({
        email:cleanEmail,
        password,
      })

      nav(
        "/dashboard",
        {
          replace:true,
        },
      )
    }catch(err){
      if(
        err instanceof Error&&
        err.message
      ){
        if(
          err.message
            .toLowerCase()
            .includes("already exists")
        ){
          setError(
            "An account with this email already exists. Sign in instead.",
          )
        }else{
          setError(err.message)
        }
      }else{
        setError(
          "We could not create your account. Please try again.",
        )
      }
    }finally{
      setBusy(false)
    }
  }

  return(
    <div className="auth-shell">
      <div className="auth-orb auth-orb-one"/>
      <div className="auth-orb auth-orb-two"/>

      <div className="auth-grid mx-auto grid w-full max-w-7xl gap-10 px-4 py-8 sm:px-6 lg:min-h-screen lg:grid-cols-[1.08fr_.92fr] lg:items-center lg:px-10">
        <section className="auth-showcase">
          <div className="auth-brand-row">
            <div className="auth-brand-mark">
              TP
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-[.32em] text-blue-300">
                TradePilot AI
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Trading intelligence workspace
              </p>
            </div>
          </div>

          <div className="mt-10 lg:mt-12">
            <div className="auth-pill auth-pill-success">
              Free workspace included
            </div>

            <h1 className="mt-6 max-w-3xl text-4xl font-semibold leading-[1.08] sm:text-5xl xl:text-6xl">
              Build your edge with
              <span className="auth-gradient-text block">
                structured intelligence.
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg sm:leading-8">
              Create your trading workspace, journal your decisions and turn
              performance data into insights you can actually use.
            </p>
          </div>

          <div className="mt-9 grid gap-4 sm:grid-cols-2">
            {[
              [
                "Professional Journal",
                "Track trades, setups, notes and outcomes in one workspace.",
              ],
              [
                "Advanced Analytics",
                "Measure performance, risk, consistency and behaviour.",
              ],
              [
                "AI Trading Coach",
                "Get analytical feedback on your process and psychology.",
              ],
              [
                "Strategy Brain",
                "Build, review and improve structured trading strategies.",
              ],
            ].map(([title,description])=>(
              <div
                key={title}
                className="auth-feature-card"
              >
                <div className="auth-check">
                  <Check className="size-4"/>
                </div>

                <div>
                  <p className="text-sm font-semibold text-slate-200">
                    {title}
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    {description}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="auth-free-card mt-8">
            <div>
              <p className="text-xs uppercase tracking-[.22em] text-emerald-300">
                Start free
              </p>

              <p className="mt-2 text-lg font-semibold">
                Your workspace is ready before you upgrade.
              </p>

              <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
                Create an account and begin with TradePilot AI Free.
                Upgrade only when you want additional Pro or Premium intelligence.
              </p>
            </div>

            <div className="auth-free-badge">
              R0
              <span>FREE</span>
            </div>
          </div>

          <p className="mt-6 max-w-2xl text-xs leading-6 text-slate-600">
            TradePilot AI provides analytical and educational tools and does not
            guarantee profitability, investment results or trading performance.
          </p>
        </section>

        <section className="mx-auto w-full max-w-md">
          <form
            onSubmit={sub}
            className="auth-card"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[.25em] text-blue-300">
                  Create workspace
                </p>

                <h2 className="mt-4 text-3xl font-semibold">
                  Start your journey
                </h2>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Your account begins on the Free plan.
                </p>
              </div>

              <div className="auth-plan-chip">
                FREE
              </div>
            </div>

            <div className="mt-7">
              <label className="auth-label">
                Email address
              </label>

              <input
                className="auth-input"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                value={email}
                onChange={e=>setEmail(e.target.value)}
                required
              />

              <label className="auth-label mt-5">
                Password
              </label>

              <input
                className="auth-input"
                type="password"
                placeholder="Minimum 8 characters"
                autoComplete="new-password"
                minLength={8}
                value={password}
                onChange={e=>setPassword(e.target.value)}
                required
              />

              <label className="auth-label mt-5">
                Confirm password
              </label>

              <input
                className="auth-input"
                type="password"
                placeholder="Repeat your password"
                autoComplete="new-password"
                minLength={8}
                value={confirmPassword}
                onChange={e=>setConfirmPassword(e.target.value)}
                required
              />
            </div>

            <label className="auth-terms">
              <input
                type="checkbox"
                checked={acceptedTerms}
                onChange={e=>setAcceptedTerms(e.target.checked)}
                className="mt-0.5 size-4 shrink-0 accent-blue-500"
              />

              <span className="text-sm leading-6 text-slate-400">
                I agree to the TradePilot AI Terms & Conditions
                and acknowledge that trading involves financial risk.
              </span>
            </label>

            {error&&(
              <div className="mt-4 rounded-2xl border border-red-400/10 bg-red-400/10 p-3 text-sm text-red-300">
                {error}
              </div>
            )}

            <button
              disabled={busy}
              className="auth-primary-button"
            >
              {busy
                ?"Creating workspace..."
                :"Create free account"}
            </button>

            <div className="mt-5 grid grid-cols-3 gap-2 text-center">
              {[
                ["Free","Start"],
                ["Secure","Account"],
                ["Instant","Access"],
              ].map(([top,bottom])=>(
                <div
                  key={top}
                  className="rounded-xl border border-white/[.05] bg-white/[.02] px-2 py-3"
                >
                  <p className="text-xs font-semibold text-slate-300">
                    {top}
                  </p>
                  <p className="mt-1 text-[10px] uppercase tracking-[.14em] text-slate-600">
                    {bottom}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-6 border-t border-white/[.07] pt-6 text-center">
              <span className="text-sm text-slate-500">
                Already have an account?
              </span>

              <Link
                to="/login"
                className="ml-2 text-sm font-semibold text-blue-300 transition hover:text-blue-200"
              >
                Sign in
              </Link>
            </div>
          </form>
        </section>
      </div>
    </div>
  )
}

const Money=({v}:{v?:number})=><>{new Intl.NumberFormat("en-ZA",{style:"currency",currency:"ZAR"}).format(v||0)}</>
export function Dashboard(){const q=useQuery({queryKey:["dashboard"],queryFn:dashboard});if(q.isLoading)return <div className="premium-card flex min-h-[320px] items-center justify-center rounded-[2rem] p-8"><div className="text-center"><div className="mx-auto size-10 animate-spin rounded-full border-2 border-white/10 border-t-blue-400"></div><h2 className="mt-5 text-xl font-semibold">Loading your dashboard</h2><p className="mt-2 text-sm text-slate-400">Preparing your latest trading performance and insights.</p></div></div>;if(q.isError)return <div className="premium-card flex min-h-[320px] items-center justify-center rounded-[2rem] p-8"><div className="max-w-md text-center"><div className="mx-auto grid size-12 place-items-center rounded-2xl bg-red-400/10 text-xl font-semibold text-red-300">!</div><h2 className="mt-5 text-2xl font-semibold">Unable to load your dashboard</h2><p className="mt-3 text-slate-400">We couldn't retrieve your trading data. Check your connection and try again.</p><button type="button" onClick={()=>q.refetch()} className="mt-6 rounded-2xl bg-blue-500 px-5 py-3 font-semibold transition hover:bg-blue-400">Try again</button></div></div>;const d=q.data||{},s=d.summary||{},i=d.intelligence||{},eq=d.equity_curve||[];return <div className="space-y-6"><section className="premium-card grid-surface rounded-[2rem] p-5 sm:p-8"><p className="text-xs uppercase tracking-[.25em] text-blue-300">AI performance brief</p><h2 className="mt-4 text-3xl font-semibold sm:text-4xl">{i.headline?.title||"Your trading intelligence is ready."}</h2><p className="mt-3 text-slate-400">{i.headline?.message||"Performance analysis is active."}</p></section><section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{[["Net Profit",<Money v={s.net_profit}/>],["Win Rate",`${s.win_rate||0}%`],["Profit Factor",s.profit_factor||0],["Trader DNA",`${i.scorecard?.overall||0}/100`]].map(([a,b])=><div key={String(a)} className="premium-card rounded-3xl p-5"><p className="text-sm text-slate-500">{a}</p><p className="mt-3 text-3xl font-semibold">{b}</p></div>)}</section><div className="premium-card rounded-[2rem] p-5 sm:p-6"><h3 className="text-xl font-semibold">Equity curve</h3><div className="mt-5 h-64 sm:h-80">{eq.length?<ResponsiveContainer width="100%" height="100%"><AreaChart data={eq}><CartesianGrid stroke="rgba(148,163,184,.08)"/><XAxis dataKey="date"/><YAxis/><Tooltip/><Area type="monotone" dataKey="balance" stroke="#6d8dff" fill="#4f7cff33"/></AreaChart></ResponsiveContainer>:<div className="grid h-full place-items-center text-slate-500">No equity data yet</div>}</div></div></div>}
const empty={broker:"Manual",ticket:"",pair:"XAUUSD",direction:"BUY" as "BUY"|"SELL",entry:"",exit_price:"",stop_loss:"",take_profit:"",lot_size:"",profit:"",strategy:"",emotion:"",notes:""}
export function Trades(){const qc=useQueryClient(),q=useQuery({queryKey:["trades"],queryFn:trades});const [search,setSearch]=useState(""),[open,setOpen]=useState(false),[editing,setEditing]=useState<Trade|null>(null),[form,setForm]=useState(empty),[review,setReview]=useState<any>(null);const add=useMutation({mutationFn:addTrade,onSuccess:()=>{qc.invalidateQueries({queryKey:["trades"]});setOpen(false)}}),edit=useMutation({mutationFn:({id,p}:{id:number;p:Partial<TradePayload>})=>editTrade(id,p),onSuccess:()=>{qc.invalidateQueries({queryKey:["trades"]});setOpen(false)}}),del=useMutation({mutationFn:removeTrade,onSuccess:()=>qc.invalidateQueries({queryKey:["trades"]})});const all=q.data?.trades||[],filtered=useMemo(()=>all.filter(t=>[t.pair,t.strategy,t.broker,t.ticket].filter(Boolean).some(v=>String(v).toLowerCase().includes(search.toLowerCase()))),[all,search]);function oe(t:Trade){setEditing(t);setForm({broker:t.broker||"",ticket:t.ticket||"",pair:t.pair,direction:t.direction,entry:String(t.entry),exit_price:String(t.exit_price??""),stop_loss:String(t.stop_loss),take_profit:String(t.take_profit),lot_size:String(t.lot_size??""),profit:String(t.profit??""),strategy:t.strategy||"",emotion:t.emotion||"",notes:t.notes||""});setOpen(true)}async function sub(e:FormEvent){e.preventDefault();const p:TradePayload={broker:form.broker||null,ticket:form.ticket||null,pair:form.pair,direction:form.direction,entry:Number(form.entry),exit_price:form.exit_price?Number(form.exit_price):null,stop_loss:Number(form.stop_loss),take_profit:Number(form.take_profit),lot_size:form.lot_size?Number(form.lot_size):null,profit:form.profit?Number(form.profit):null,commission:0,swap:0,strategy:form.strategy||null,emotion:form.emotion||null,notes:form.notes||null,imported:false};editing?await edit.mutateAsync({id:editing.id,p}):await add.mutateAsync(p)}return <div className="space-y-6"><section className="premium-card grid-surface rounded-[2rem] p-5 sm:p-8"><div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between"><div><p className="text-xs uppercase tracking-[.25em] text-blue-300">Trade journal</p><h2 className="mt-4 text-3xl font-semibold sm:text-4xl">Every trade becomes intelligence.</h2></div><button onClick={()=>{setEditing(null);setForm(empty);setOpen(true)}} className="flex h-fit w-full items-center justify-center gap-2 rounded-2xl bg-blue-500 px-5 py-3 font-semibold sm:w-auto"><Plus className="size-4"/>Add trade</button></div></section><div className="premium-card flex items-center gap-3 rounded-3xl px-4"><Search className="size-4"/><input value={search} onChange={e=>setSearch(e.target.value)} className="w-full bg-transparent py-3 outline-none" placeholder="Search trades..."/></div><div className="premium-card overflow-x-auto rounded-[2rem]"><table className="w-full min-w-[900px]"><thead><tr>{["Market","Direction","Entry","Exit","Profit","Strategy","Actions"].map(x=><th key={x} className="px-5 py-4 text-left text-xs uppercase text-slate-500">{x}</th>)}</tr></thead><tbody>{q.isLoading?<tr><td colSpan={7} className="px-6 py-16"><div className="text-center"><div className="mx-auto size-8 animate-spin rounded-full border-2 border-white/10 border-t-blue-400"></div><p className="mt-4 font-medium">Loading your trades</p><p className="mt-1 text-sm text-slate-500">Retrieving your trading journal...</p></div></td></tr>:q.isError?<tr><td colSpan={7} className="px-6 py-16"><div className="mx-auto max-w-md text-center"><div className="mx-auto grid size-10 place-items-center rounded-xl bg-red-400/10 font-semibold text-red-300">!</div><p className="mt-4 font-semibold">Unable to load your trades</p><p className="mt-2 text-sm text-slate-400">We couldn't retrieve your trading journal. Check your connection and try again.</p><button type="button" onClick={()=>q.refetch()} className="mt-5 rounded-2xl bg-blue-500 px-5 py-2.5 text-sm font-semibold transition hover:bg-blue-400">Try again</button></div></td></tr>:filtered.length===0?<tr><td colSpan={7} className="px-6 py-16"><div className="mx-auto max-w-md text-center"><div className="mx-auto grid size-12 place-items-center rounded-2xl bg-blue-400/10 text-blue-300"><BrainCircuit className="size-5"/></div><p className="mt-4 font-semibold">{search?"No matching trades":"No trades yet"}</p><p className="mt-2 text-sm text-slate-400">{search?"Try a different market, strategy, broker or ticket.":"Add your first trade to start building your journal and trading intelligence."}</p>{!search&&<button type="button" onClick={()=>{setEditing(null);setForm(empty);setOpen(true)}} className="mt-5 inline-flex items-center gap-2 rounded-2xl bg-blue-500 px-5 py-2.5 text-sm font-semibold transition hover:bg-blue-400"><Plus className="size-4"/>Add first trade</button>}</div></td></tr>:filtered.map(t=><tr key={t.id} className="border-t border-white/[.06]"><td className="px-5 py-4"><b>{t.pair}</b><div className="text-xs text-slate-500">{t.broker||"Manual"}</div></td><td className={`px-5 py-4 ${t.direction==="BUY"?"text-emerald-300":"text-red-300"}`}>{t.direction}</td><td className="px-5 py-4">{t.entry}</td><td className="px-5 py-4">{t.exit_price??"-"}</td><td className={`px-5 py-4 ${(t.profit||0)>=0?"text-emerald-300":"text-red-300"}`}>{t.profit??0}</td><td className="px-5 py-4">{t.strategy||"Unspecified"}</td><td className="px-5 py-4"><div className="flex gap-2"><button onClick={async()=>setReview({trade:t,data:await reviewTrade(t.id)})} className="rounded-xl bg-blue-400/10 p-2"><BrainCircuit className="size-4"/></button><button onClick={()=>oe(t)} className="rounded-xl bg-white/[.04] p-2"><Pencil className="size-4"/></button><button onClick={()=>confirm("Delete trade?")&&del.mutate(t.id)} className="rounded-xl bg-red-400/10 p-2 text-red-300"><Trash2 className="size-4"/></button></div></td></tr>)}</tbody></table></div>{open&&<div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><form onSubmit={sub} className="premium-card max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] p-5 sm:p-7"><h3 className="text-2xl font-semibold">{editing?"Edit trade":"Add trade"}</h3><div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">{(["pair","broker","ticket"] as const).map(k=><input key={k} placeholder={k} className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>) }<select className="rounded-2xl bg-[#0b1120] px-4 py-3" value={form.direction} onChange={e=>setForm({...form,direction:e.target.value as any})}><option>BUY</option><option>SELL</option></select></div><div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-5">{(["entry","exit_price","stop_loss","take_profit","lot_size"] as const).map(k=><input key={k} type="number" step="any" placeholder={k} className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>)}</div><div className="mt-4 grid gap-4 md:grid-cols-3">{(["profit","strategy","emotion"] as const).map(k=><input key={k} placeholder={k} className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>)}</div><textarea className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" rows={4} placeholder="Notes" value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})}/><div className="mt-5 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end"><button type="button" onClick={()=>setOpen(false)} className="rounded-2xl border border-white/10 px-5 py-3">Cancel</button><button className="rounded-2xl bg-blue-500 px-5 py-3">Save</button></div></form></div>}{review&&<div className="fixed inset-0 z-50 flex justify-end bg-black/60"><aside className="h-full w-full max-w-xl overflow-y-auto bg-[#090f1c] p-5 sm:p-8"><button onClick={()=>setReview(null)} className="float-right">Close</button><h3 className="text-2xl font-semibold">AI Review - {review.trade.pair}</h3><div className="mt-6 premium-card rounded-3xl p-5"><div className="text-4xl text-blue-300">{review.data.trade_score}</div><p className="mt-2">{review.data.summary}</p></div><h4 className="mt-6 text-emerald-300">Strengths</h4>{review.data.strengths?.map((x:string)=><p key={x} className="mt-2 rounded-2xl bg-emerald-400/[.05] p-3">{x}</p>)}<h4 className="mt-6 text-red-300">Mistakes</h4>{review.data.mistakes?.map((x:string)=><p key={x} className="mt-2 rounded-2xl bg-red-400/[.05] p-3">{x}</p>)}</aside></div>}</div>}
export function Analytics(){const q=useQuery({queryKey:["analysis"],queryFn:analysis});if(q.isLoading)return <Page title="Analytics" subtitle="Know exactly what drives your results."><div className="grid min-h-[420px] place-items-center"><div className="text-center"><div className="mx-auto size-10 animate-spin rounded-full border-2 border-white/10 border-t-blue-400"></div><p className="mt-4 font-semibold">Loading analytics</p><p className="mt-1 text-sm text-slate-500">Calculating your trading performance...</p></div></div></Page>;if(q.isError)return <Page title="Analytics" subtitle="Know exactly what drives your results."><div className="grid min-h-[420px] place-items-center"><div className="max-w-md text-center"><div className="mx-auto grid size-12 place-items-center rounded-2xl bg-red-400/10 text-xl font-bold text-red-300">!</div><p className="mt-4 text-lg font-semibold">Unable to load analytics</p><p className="mt-2 text-sm text-slate-400">Your performance data could not be retrieved. Please try again.</p><button onClick={()=>q.refetch()} className="mt-5 rounded-2xl bg-blue-500 px-5 py-3 font-semibold">Try again</button></div></div></Page>;const d=q.data||{},p=d.performance||{},r=d.risk||{},ps=d.psychology||{},c=d.consistency?.score||{};return <Page title="Analytics" subtitle="Know exactly what drives your results."><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{[["Win Rate",`${p.win_rate??0}%`],["Profit Factor",p.profit_factor??0],["Expectancy",r.expectancy??0],["Max Drawdown",r.maximum_drawdown??0],["Discipline",d.trader_dna?.sufficient_data===false?"Not enough data yet":(ps.discipline_score??0)],["Consistency",d.trader_dna?.sufficient_data===false?"Not enough data yet":(c.overall_score??0)]].map(([a,b])=><div key={String(a)} className="premium-card rounded-3xl p-6"><p className="text-slate-500">{a}</p><p className="mt-3 text-3xl font-semibold">{String(b)}</p></div>)}</div></Page>}
export function DNA(){const q=useQuery({queryKey:["analysis"],queryFn:analysis});if(q.isLoading)return <Page title="Trader DNA" subtitle="Building your trading profile."><div className="grid min-h-[420px] place-items-center"><div className="text-center"><div className="mx-auto size-10 animate-spin rounded-full border-2 border-white/10 border-t-blue-400"></div><p className="mt-4 font-semibold">Building Trader DNA</p><p className="mt-1 text-sm text-slate-500">Analyzing your strengths and weaknesses...</p></div></div></Page>;if(q.isError)return <Page title="Trader DNA" subtitle="Your trading profile is temporarily unavailable."><div className="grid min-h-[420px] place-items-center"><div className="max-w-md text-center"><div className="mx-auto grid size-12 place-items-center rounded-2xl bg-red-400/10 text-xl font-bold text-red-300">!</div><p className="mt-4 text-lg font-semibold">Unable to build Trader DNA</p><p className="mt-2 text-sm text-slate-400">We couldn't retrieve your psychology profile. Please try again.</p><button onClick={()=>q.refetch()} className="mt-5 rounded-2xl bg-blue-500 px-5 py-3 font-semibold">Try again</button></div></div></Page>;const d=q.data?.trader_dna||{},hasData=(d.strengths?.length||0)+(d.weaknesses?.length||0)>0;return <Page title="Trader DNA" subtitle={d.profile||"Developing Trader"}>{hasData?<div className="grid gap-6 lg:grid-cols-2"><List title="Strengths" items={d.strengths||[]} good/><List title="Weaknesses" items={d.weaknesses||[]}/></div>:<div className="premium-card grid min-h-[320px] place-items-center rounded-[2rem] p-8"><div className="max-w-md text-center"><div className="mx-auto grid size-14 place-items-center rounded-2xl bg-blue-400/10 text-blue-300"><BrainCircuit className="size-7"/></div><p className="mt-5 text-xl font-semibold">Your Trader DNA is still developing</p><p className="mt-2 text-sm text-slate-400">Complete and review more trades to unlock personalized strengths, weaknesses and psychology insights.</p></div></div>}</Page>}
function List({title,items,good}:{title:string;items:string[];good?:boolean}){return <div className="premium-card rounded-3xl p-6"><h3 className={`text-xl ${good?"text-emerald-300":"text-red-300"}`}>{title}</h3>{items.map(x=><div key={x} className="mt-3 rounded-2xl bg-white/[.03] p-4">{x}</div>)}</div>}
export function Coach(){const [msgs,setMsgs]=useState<any[]>([{role:"assistant",text:"Ask me about your performance, psychology or priorities."}]),[text,setText]=useState(""),[busy,setBusy]=useState(false);async function sub(e:FormEvent){e.preventDefault();const t=text.trim();if(!t||busy)return;setMsgs(m=>[...m,{role:"user",text:t}]);setText("");setBusy(true);try{const r=await coach(t);setMsgs(m=>[...m,{role:"assistant",text:r.answer||"Analysis complete."}])}catch{setMsgs(m=>[...m,{role:"assistant",text:"AI Coach is temporarily unavailable. Please try again in a moment."}])}finally{setBusy(false)}}return <div className="premium-card flex min-h-[72vh] flex-col rounded-[2rem] p-5 sm:p-6"><div><p className="text-xs uppercase tracking-[.25em] text-blue-300">Trading intelligence</p><h2 className="mt-3 text-2xl font-semibold sm:text-3xl">AI Coach</h2><p className="mt-2 text-sm text-slate-400">Ask about your performance, risk, psychology or trading priorities.</p></div><div className="mt-6 flex-1 space-y-4">{msgs.map((m,i)=><div key={i} className={`max-w-[90%] rounded-3xl p-4 sm:max-w-[85%] ${m.role==="user"?"ml-auto bg-blue-500":"bg-white/[.05]"}`}>{m.text}</div>)}{busy&&<div className="max-w-[90%] rounded-3xl bg-white/[.05] p-4 sm:max-w-[85%]"><div className="flex items-center gap-3 text-slate-400"><div className="size-4 animate-spin rounded-full border-2 border-white/10 border-t-blue-400"></div><span className="text-sm">Analyzing your trading data...</span></div></div>}</div><form onSubmit={sub} className="mt-5 flex flex-col gap-3 sm:flex-row"><input disabled={busy} className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3 outline-none disabled:cursor-not-allowed disabled:opacity-60" value={text} onChange={e=>setText(e.target.value)} placeholder="Ask about your trading performance..."/><button disabled={busy||!text.trim()} className="w-full rounded-2xl bg-blue-500 px-5 py-3 font-semibold transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto">{busy?"Thinking...":"Send"}</button></form><p className="mt-3 text-xs text-slate-500">AI insights are analytical and educational, not financial advice or guaranteed trading outcomes.</p></div>}
export function Reports(){const w=useQuery({queryKey:["weekly"],queryFn:weekly}),m=useQuery({queryKey:["monthly"],queryFn:monthly});const reports=[["Weekly",w],["Monthly",m]] as const;return <Page title="Reports" subtitle="Weekly and monthly performance reviews."><div className="grid gap-6 lg:grid-cols-2">{reports.map(([t,q])=><div key={t} className="premium-card min-h-[260px] rounded-3xl p-5 sm:p-6"><p className="text-blue-300">{t} review</p>{q.isLoading?<div className="grid min-h-[190px] place-items-center"><div className="text-center"><div className="mx-auto size-8 animate-spin rounded-full border-2 border-white/10 border-t-blue-400"></div><p className="mt-4 text-sm text-slate-400">Preparing your {t.toLowerCase()} report...</p></div></div>:q.isError?<div className="grid min-h-[190px] place-items-center"><div className="text-center"><div className="mx-auto grid size-10 place-items-center rounded-xl bg-red-400/10 font-semibold text-red-300">!</div><p className="mt-4 font-semibold">Report unavailable</p><p className="mt-2 text-sm text-slate-400">We couldn't retrieve this report.</p><button type="button" onClick={()=>q.refetch()} className="mt-4 rounded-2xl bg-blue-500 px-4 py-2 text-sm font-semibold transition hover:bg-blue-400">Try again</button></div></div>:q.data?<>{(q.data as any).grade==null?<><p className="mt-4 text-xl font-semibold">Not enough data yet</p><p className="mt-2 text-slate-400">Log {(q.data as any).trades_needed||"more"} more completed trade(s) to unlock a graded review.</p></>:<><p className="mt-4 text-3xl font-semibold sm:text-4xl">{q.data.grade}</p><p className="mt-2 text-slate-400">Score {q.data.score}/100</p></>}<p className="mt-5">{q.data.summary||"Your report is ready."}</p></>:<div className="grid min-h-[190px] place-items-center"><div className="max-w-sm text-center"><p className="font-semibold">No {t.toLowerCase()} report yet</p><p className="mt-2 text-sm text-slate-400">Keep logging trades and your performance review will appear here when reporting data is available.</p></div></div>}</div>)}</div></Page>}
export function Strategy(){const [saved,setSaved]=useState(false);return <Page title="Strategy Lab" subtitle="Teach TradePilot AI exactly how you trade."><div className="grid gap-6 xl:grid-cols-[1.2fr_.8fr]"><div className="premium-card rounded-3xl p-6"><input className="w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" defaultValue="London Breakout"/><textarea className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" rows={10} defaultValue={`Trade London session only
Wait for liquidity sweep
Require structure shift
Risk maximum 0.5%`}/><div className="mt-4 rounded-2xl border border-dashed border-white/10 p-8 text-center"><Upload className="mx-auto"/><p className="mt-3">Upload charts, PDFs or notes</p><input type="file" multiple className="mt-4"/></div><button onClick={()=>setSaved(true)} className="mt-4 rounded-2xl bg-blue-500 px-5 py-3">Save strategy</button></div><div className="premium-card rounded-3xl p-6"><h3 className="text-xl font-semibold">Approval-based automation</h3><p className="mt-3 text-slate-400">AI prepares a setup against your rules. You approve before execution. Unattended trading stays disabled until broker and risk controls are validated.</p>{saved&&<div className="mt-5 rounded-2xl bg-emerald-400/10 p-4 text-emerald-300">Strategy profile saved locally.</div>}</div></div></Page>}
export function LegacyPartnersOld(){const offers=[["Recommended Broker","MT5 - tracked minimum deposit"],["Prop Firm Challenge","Evaluation and partner signup"],["Lloyd Traders LTD","Trading signals coming soon"],["Affiliate Marketplace","Books, tools and education"]];return <Page title="Brokers & Partners" subtitle="Recommended brokers, prop firms and partner resources."><div className="grid gap-5 md:grid-cols-2">{offers.map(([n,d])=><div key={n} className="premium-card rounded-3xl p-6"><h3 className="text-xl font-semibold">{n}</h3><p className="mt-3 text-slate-400">{d}</p><button className="mt-5 flex items-center gap-2 rounded-2xl border border-white/10 px-4 py-2"><ExternalLink className="size-4"/>View offer</button></div>)}</div><div className="mt-6 rounded-3xl bg-amber-400/[.05] p-5 text-sm text-slate-400">Affiliate disclosure: TradePilot AI may earn commissions through partner links. Trading involves risk.</div></Page>}
export function Billing(){
  const {user}=useAuth()
  const qc=useQueryClient()

  const subscriptionQuery=useQuery({
    queryKey:["subscription"],
    queryFn:mySubscription,
  })

  const [busyPlan,setBusyPlan]=useState("")
  const [message,setMessage]=useState("")

  const subscription=subscriptionQuery.data

  async function choosePlan(
    plan:"pro"|"premium"
  ){
    setBusyPlan(plan)
    setMessage("")

    try{
      const result=
        await createPayPalSubscription(plan)

      if(!result.approval_url){
        throw new Error(
          "PayPal approval URL missing."
        )
      }

      window.location.href=
        result.approval_url
    }catch(err:any){
      const detail=
        err?.response?.data?.detail

      setMessage(
        typeof detail==="string"
          ? detail
          : detail?.message ||
            "Unable to start PayPal checkout."
      )
    }finally{
      setBusyPlan("")
    }
  }

  async function cancelPlan(){
    const confirmed=window.confirm(
      "Cancel your subscription? Future PayPal renewals will be stopped."
    )

    if(!confirmed)return

    setMessage("")

    try{
      const result=
        await cancelSubscription()

      setMessage(
        result.message ||
        "Subscription cancelled."
      )

      await qc.invalidateQueries({
        queryKey:["subscription"]
      })

      await subscriptionQuery.refetch()
    }catch(err:any){
      const detail=
        err?.response?.data?.detail

      setMessage(
        typeof detail==="string"
          ? detail
          : detail?.message ||
            "Unable to cancel subscription."
      )
    }
  }

  const plans=[
    {
      name:"Free",
      code:"free",
      launchPrice:"$0",
      normalPrice:"",
      detail:"Forever",
      description:
        "Start tracking your trading journey with the essential TradePilot tools.",
      features:[
        "Trade journal",
        "Core performance tracking",
        "Basic trading insights",
      ],
    },
    {
      name:"Pro",
      code:"pro",
      launchPrice:"$10",
      normalPrice:"$19.99/month",
      detail:"First month",
      description:
        "Built for active traders who want deeper analysis and smarter decision support.",
      features:[
        "Advanced reports",
        "Strategy tools",
        "AI Coach access",
        "Enhanced analytics",
      ],
    },
    {
      name:"Premium",
      code:"premium",
      launchPrice:"$10",
      normalPrice:"$29.99/month",
      detail:"First month",
      description:
        "Unlock TradePilot AI's most advanced analysis and premium intelligence tools.",
      features:[
        "Everything in Pro",
        "Premium AI analysis",
        "Advanced Trader DNA",
        "Priority premium features",
      ],
    },
  ] as const

  const currentPlan=
    String(
      subscription?.plan ||
      user?.plan ||
      "free"
    ).toLowerCase()

  const subscriptionStatus=
    String(
      subscription?.status ||
      "inactive"
    ).toLowerCase()

  const statusStyle=
    subscriptionStatus==="active"
      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
      : subscriptionStatus==="approval_pending"
        ? "border-amber-400/20 bg-amber-400/10 text-amber-300"
        : "border-white/10 bg-white/[.04] text-slate-300"

  return (
    <Page
      title="Billing"
      subtitle="Choose the TradePilot AI plan that fits your trading journey."
    >
      <section className="premium-card overflow-hidden rounded-[2rem] border border-blue-400/10">
        <div className="grid-surface p-6 sm:p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="inline-flex items-center rounded-full border border-blue-400/20 bg-blue-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[.18em] text-blue-300">
                Membership
              </div>

              <h2 className="mt-4 text-2xl font-semibold sm:text-3xl">
                Your TradePilot AI plan
              </h2>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                Manage your membership and upgrade securely through PayPal.
                Your trading account and billing account remain separate.
              </p>
            </div>

            {subscriptionQuery.isLoading ? (
              <div className="rounded-2xl border border-white/10 bg-white/[.03] px-5 py-4 text-sm text-slate-400">
                Loading subscription...
              </div>
            ) : (
              <div className="w-full rounded-2xl border border-white/10 bg-black/20 p-5 sm:min-w-[220px] lg:w-auto">
                <p className="text-xs uppercase tracking-[.18em] text-slate-500">
                  Current plan
                </p>

                <div className="mt-2 flex items-center justify-between gap-3">
                  <p className="text-2xl font-semibold capitalize text-white">
                    {currentPlan}
                  </p>

                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-medium capitalize ${statusStyle}`}
                  >
                    {subscriptionStatus}
                  </span>
                </div>

                {subscription?.next_billing_at && (
                  <p className="mt-3 text-xs text-slate-500">
                    Next billing{" "}
                    <span className="text-slate-300">
                      {new Date(
                        subscription.next_billing_at
                      ).toLocaleDateString()}
                    </span>
                  </p>
                )}
              </div>
            )}
          </div>

          {subscription &&
           subscription.plan!=="free" &&
           subscription.status!=="cancelled" &&
           subscription.status!=="canceled" && (
            <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/[.06] bg-white/[.02] p-4">
              <div>
                <p className="text-sm font-medium text-slate-200">
                  Active PayPal membership
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  You can stop future renewals whenever you choose.
                </p>
              </div>

              <button
                type="button"
                onClick={cancelPlan}
                className="rounded-xl border border-red-400/30 px-4 py-2 text-sm font-medium text-red-300 transition hover:bg-red-400/10"
              >
                Cancel subscription
              </button>
            </div>
          )}
        </div>
      </section>

      {subscriptionQuery.isError && (
        <div className="rounded-2xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-200">
          We could not load your subscription details. Please refresh and try again.
        </div>
      )}

      {message && (
        <div className="rounded-2xl border border-blue-400/20 bg-blue-400/10 p-4 text-sm text-blue-200">
          {message}
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-3">
        {plans.map(plan=>{
          const isCurrent=
            currentPlan===plan.code &&
            (
              plan.code==="free" ||
              subscriptionStatus==="active"
            )

          const isPremium=
            plan.code==="premium"

          return (
            <div
              key={plan.code}
              className={`premium-card relative flex h-full flex-col overflow-hidden rounded-[2rem] p-5 transition sm:p-6 ${
                isPremium
                  ? "border border-blue-400/30 shadow-[0_0_50px_rgba(59,130,246,0.08)]"
                  : "border border-white/[.06]"
              }`}
            >
              {isPremium && (
                <div className="absolute right-5 top-5 rounded-full bg-blue-500 px-3 py-1 text-[11px] font-semibold uppercase tracking-[.12em] text-white">
                  Most advanced
                </div>
              )}

              <div>
                <p className="text-sm font-medium text-blue-300">
                  TradePilot AI
                </p>

                <h3 className="mt-2 text-2xl font-semibold">
                  {plan.name}
                </h3>

                <p className="mt-3 min-h-[48px] text-sm leading-6 text-slate-400">
                  {plan.description}
                </p>
              </div>

              <div className="mt-6 border-y border-white/[.06] py-5">
                {plan.code!=="free" && (
                  <div className="mb-3 inline-flex rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-300">
                    Launch Offer
                  </div>
                )}

                <div className="flex items-end gap-2">
                  <p className="text-4xl font-semibold tracking-tight">
                    {plan.launchPrice}
                  </p>

                  {plan.code!=="free" && (
                    <span className="mb-1 text-sm text-slate-500">
                      USD
                    </span>
                  )}
                </div>

                <p className="mt-1 text-sm text-slate-500">
                  {plan.detail}
                </p>

                {plan.normalPrice && (
                  <p className="mt-3 text-sm text-slate-400">
                    Then{" "}
                    <span className="font-medium text-slate-200">
                      {plan.normalPrice}
                    </span>
                  </p>
                )}
              </div>

              <div className="mt-5 flex-1 space-y-3">
                {plan.features.map(feature=>(
                  <div
                    key={feature}
                    className="flex items-center gap-3 text-sm text-slate-300"
                  >
                    <span className="grid size-5 shrink-0 place-items-center rounded-full bg-emerald-400/10 text-emerald-300">
                      <Check className="size-3" strokeWidth={3} />
                    </span>

                    <span>{feature}</span>
                  </div>
                ))}
              </div>

              <div className="mt-7">
                {plan.code==="free" ? (
                  <button
                    type="button"
                    disabled
                    className="w-full rounded-2xl border border-white/10 bg-white/[.04] py-3 font-medium text-slate-500"
                  >
                    {currentPlan==="free"
                      ? "Current plan"
                      : "Free plan"}
                  </button>
                ) : (
                  <button
                    type="button"
                    disabled={
                      busyPlan!=="" ||
                      subscriptionStatus==="active"
                    }
                    onClick={()=>
                      choosePlan(plan.code)
                    }
                    className={`w-full rounded-2xl py-3 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${
                      isPremium
                        ? "bg-blue-500 text-white hover:bg-blue-400"
                        : "border border-blue-400/30 bg-blue-500/10 text-blue-200 hover:bg-blue-500/20"
                    }`}
                  >
                    {isCurrent
                      ? "Current plan"
                      : busyPlan===plan.code
                        ? "Opening PayPal..."
                        : `Choose ${plan.name}`}
                  </button>
                )}

                {plan.code!=="free" && (
                  <p className="mt-3 text-center text-xs text-slate-500">
                    Secure recurring billing through PayPal - Cancel anytime
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <section className="premium-card rounded-[2rem] border border-white/[.06] p-5 sm:p-6">
        <div className="grid gap-6 md:grid-cols-3">
          <div>
            <p className="text-xs uppercase tracking-[.16em] text-slate-500">
              Payment provider
            </p>

            <p className="mt-2 font-medium text-slate-200">
              PayPal
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Secure recurring subscription billing.
            </p>
          </div>

          <div>
            <p className="text-xs uppercase tracking-[.16em] text-slate-500">
              Billing currency
            </p>

            <p className="mt-2 font-medium text-slate-200">
              USD
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Your preferred app currency is{" "}
              {user?.preferred_currency || "USD"}.
            </p>
          </div>

          <div>
            <p className="text-xs uppercase tracking-[.16em] text-slate-500">
              Subscription control
            </p>

            <p className="mt-2 font-medium text-slate-200">
              Cancel anytime
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Manage future renewals directly from TradePilot AI.
            </p>
          </div>
        </div>

        <div className="mt-6 border-t border-white/[.06] pt-5 text-xs leading-5 text-slate-500">
          Trading involves risk. TradePilot AI provides analytical and educational
          decision-support tools and does not guarantee profitability or future
          trading performance.
        </div>
      </section>
    </Page>
  )
}

export function Settings(){
  const {user}=useAuth()
  const {t,i18n}=useTranslation()

  const [language,setLanguage]=useState(
    user?.preferred_language || "en"
  )

  const [currency,setCurrency]=useState(
    user?.preferred_currency || "USD"
  )

  const [saving,setSaving]=useState(false)
  const [message,setMessage]=useState("")

  async function savePreferences(){
    setSaving(true)
    setMessage("")

    try{
      const updated=await updatePreferences({
        preferred_language:language,
        preferred_currency:currency,
      })

      await i18n.changeLanguage(
        updated.preferred_language || language
      )

      localStorage.setItem(
        "i18nextLng",
        updated.preferred_language || language
      )

      const existing=JSON.parse(
        localStorage.getItem("tradepilot_user") || "{}"
      )

      localStorage.setItem(
        "tradepilot_user",
        JSON.stringify({
          ...existing,
          ...updated,
        })
      )

      setMessage("Preferences saved successfully.")
    }catch{
      setMessage("Unable to save preferences.")
    }finally{
      setSaving(false)
    }
  }

  return (
    <Page
      title={t("settings")}
      subtitle="Manage your profile and global application preferences."
    >
      <div className="premium-card max-w-3xl rounded-3xl p-5 sm:p-6">
        <div className="grid gap-6 md:grid-cols-2">

          <div>
            <label className="mb-2 block text-sm text-slate-400">
              {t("language")}
            </label>

            <select
              value={language}
              onChange={e=>setLanguage(e.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="en">English</option>
              <option value="af">Afrikaans</option>
              <option value="fr">Français</option>
              <option value="es">Español</option>
              <option value="pt">Português</option>
              <option value="de">Deutsch</option>
              <option value="ar">العربية</option>
              <option value="zh">中文</option>
              <option value="ja">日本語</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-400">
              {t("currency")}
            </label>

            <select
              value={currency}
              onChange={e=>setCurrency(e.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              {supportedCurrencies.map(item=>(
                <option
                  key={item.code}
                  value={item.code}
                >
                  {item.code} — {item.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.02] p-4">
          <p className="text-sm text-slate-400">
            These preferences are stored on your TradePilot AI account,
            so they can follow you across web and mobile devices.
          </p>
        </div>

        {message && (
          <p className="mt-4 text-sm text-blue-300">
            {message}
          </p>
        )}

        <button
          type="button"
          disabled={saving}
          onClick={savePreferences}
          className="mt-6 w-full rounded-2xl bg-blue-500 px-6 py-3 font-medium transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
        >
          {saving
            ? "Saving..."
            : t("savePreferences")}
        </button>
      </div>
    </Page>
  )
}
function Page({title,subtitle,children}:{title:string;subtitle:string;children:any}){return <div className="space-y-6"><section className="premium-card grid-surface rounded-[2rem] p-5 sm:p-8"><p className="text-xs uppercase tracking-[.25em] text-blue-300">TradePilot AI</p><h2 className="mt-4 text-3xl font-semibold sm:text-4xl">{title}</h2><p className="mt-3 text-slate-400">{subtitle}</p></section>{children}</div>}
export function LegacyPartnersOld2(){
  const propFirms=[
    {
      name:"VPropTrader",
      description:
        "Take a free $1,000 prop trading challenge, test your trading skills and qualify for profit sharing if successful.",
      url:"https://vproptrader.com/share/yvc3h?invite=nkd8i16c",
      badge:"Free $1,000 Challenge",
    },
    {
      name:"FundedElite",
      description:
        "Explore FundedElite prop trading challenges and funding opportunities.",
      url:"https://app.fundedelite.com?aff=AFF8683831",
      badge:"Prop Firm",
    },
    {
      name:"The5ers",
      description:
        "Explore trading programs and funding opportunities from The5ers.",
      url:"https://www.the5ers.com/?afmc=1dtk",
      badge:"Prop Firm",
    },
  ]

  const brokers=[
    {
      name:"DB Investing",
      description:
        "Recommended broker available through the TradePilot AI partner network.",
      url:"https://my.dbinvesting.com/links/go/3766",
      badge:"Recommended Broker",
    },
    {
      name:"Headway",
      description:
        "Broker option for traders looking for an accessible trading platform.",
      url:"https://headway.partners/user/signup?hwp=12eab6",
      badge:"Affordable Option",
    },
    {
      name:"XM ZA",
      description:
        "Explore XM through the TradePilot AI referral partnership.",
      url:"https://www.xmza.com/referral?token=ir4kDrpVX16S63SmNzNj3A",
      badge:"Broker",
    },
  ]

  function openPartner(
    url:string,
    name:string,
    type:"broker"|"prop_firm",
  ){
    // Later we will send this event to the backend
    // so the Admin dashboard can track partner clicks.
    console.log("Partner click",{
      name,
      type,
      url,
    })

    window.open(
      url,
      "_blank",
      "noopener,noreferrer",
    )
  }

  return (
    <Page
      title="Brokers & Prop Firms"
      subtitle="Explore TradePilot AI partner brokers and proprietary trading opportunities."
    >
      <section>
        <div className="mb-5">
          <p className="text-xs uppercase tracking-[.25em] text-blue-300">
            Funding Opportunities
          </p>

          <h3 className="mt-2 text-2xl font-semibold">
            Prop Firm Recommendations
          </h3>

          <p className="mt-2 text-sm text-slate-400">
            Explore third-party trading challenges and funding programs.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {propFirms.map(firm=>(
            <div
              key={firm.name}
              className="premium-card flex flex-col rounded-3xl p-6"
            >
              <div>
                <span className="rounded-full bg-blue-400/10 px-3 py-1 text-xs text-blue-300">
                  {firm.badge}
                </span>

                <h4 className="mt-5 text-xl font-semibold">
                  {firm.name}
                </h4>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  {firm.description}
                </p>
              </div>

              <button
                onClick={()=>
                  openPartner(
                    firm.url,
                    firm.name,
                    "prop_firm",
                  )
                }
                className="mt-6 flex items-center justify-center gap-2 rounded-2xl bg-blue-500 px-4 py-3 font-medium"
              >
                View Opportunity
                <ExternalLink className="size-4"/>
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-10">
        <div className="mb-5">
          <p className="text-xs uppercase tracking-[.25em] text-blue-300">
            Trading Partners
          </p>

          <h3 className="mt-2 text-2xl font-semibold">
            Broker Recommendations
          </h3>

          <p className="mt-2 text-sm text-slate-400">
            Explore brokers available through TradePilot AI partner links.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {brokers.map(broker=>(
            <div
              key={broker.name}
              className="premium-card flex flex-col rounded-3xl p-6"
            >
              <div>
                <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">
                  {broker.badge}
                </span>

                <h4 className="mt-5 text-xl font-semibold">
                  {broker.name}
                </h4>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  {broker.description}
                </p>
              </div>

              <button
                onClick={()=>
                  openPartner(
                    broker.url,
                    broker.name,
                    "broker",
                  )
                }
                className="mt-6 flex items-center justify-center gap-2 rounded-2xl bg-blue-500 px-4 py-3 font-medium"
              >
                Visit Broker
                <ExternalLink className="size-4"/>
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="premium-card mt-8 rounded-3xl p-5">
        <p className="text-sm leading-6 text-slate-400">
          <strong className="text-slate-200">
            Affiliate disclosure:
          </strong>{" "}
          Some links on this page are affiliate or referral links.
          TradePilot AI may receive compensation when users register
          through these links. This does not increase the price paid
          by the user.
        </p>

        <p className="mt-3 text-sm leading-6 text-slate-500">
          Trading leveraged products and participating in proprietary
          trading challenges involve financial risk. Eligibility,
          pricing, rules and services are determined by each
          independent provider. Review each provider's terms before
          opening an account or purchasing a challenge.
        </p>
      </section>
    </Page>
  )
}
