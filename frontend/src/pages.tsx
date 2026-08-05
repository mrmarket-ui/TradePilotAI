import {useMemo,useState,type FormEvent} from "react"
import {Navigate,useLocation,useNavigate} from "react-router-dom"
import {useMutation,useQuery,useQueryClient} from "@tanstack/react-query"
import {Area,AreaChart,CartesianGrid,ResponsiveContainer,Tooltip,XAxis,YAxis} from "recharts"
import {Plus,Search,Pencil,Trash2,BrainCircuit,Upload,ExternalLink} from "lucide-react"
import {useAuth} from "@/Auth"
import {useTranslation} from "react-i18next"
import {updatePreferences} from "@/api/profile/preferences"
import {supportedCurrencies} from "@/utils/currency"
import {dashboard,analysis,trades,addTrade,editTrade,removeTrade,reviewTrade,weekly,monthly,coach,createPayPalSubscription,mySubscription,cancelSubscription} from "@/api"
import type {Trade,TradePayload} from "@/types"
export function Login(){const {login,isAuthenticated}=useAuth();const nav=useNavigate(),loc=useLocation();const [email,setEmail]=useState(""),[password,setPassword]=useState(""),[error,setError]=useState(""),[busy,setBusy]=useState(false);const d=(loc.state as any)?.from||"/dashboard";if(isAuthenticated)return <Navigate to={d} replace/>;async function sub(e:FormEvent){e.preventDefault();setBusy(true);setError("");try{await login({email,password});nav(d,{replace:true})}catch{setError("Invalid email or password.")}finally{setBusy(false)}}return <div className="grid min-h-screen place-items-center bg-[#060912] p-4"><form onSubmit={sub} className="premium-card w-full max-w-md rounded-[2rem] p-8"><p className="text-xs uppercase tracking-[.25em] text-blue-300">TradePilot AI</p><h1 className="mt-4 text-3xl font-semibold">Welcome back</h1><input className="mt-8 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required/><input className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required/>{error&&<div className="mt-4 rounded-2xl bg-red-400/10 p-3 text-red-300">{error}</div>}<button className="mt-5 w-full rounded-2xl bg-blue-500 px-4 py-3 font-semibold">{busy?"Signing in...":"Enter workspace"}</button></form></div>}
const Money=({v}:{v?:number})=><>{new Intl.NumberFormat("en-ZA",{style:"currency",currency:"ZAR"}).format(v||0)}</>
export function Dashboard(){const q=useQuery({queryKey:["dashboard"],queryFn:dashboard});if(q.isLoading)return <p>Loading...</p>;const d=q.data||{},s=d.summary||{},i=d.intelligence||{},eq=d.equity_curve||[];return <div className="space-y-6"><section className="premium-card grid-surface rounded-[2rem] p-8"><p className="text-xs uppercase tracking-[.25em] text-blue-300">AI performance brief</p><h2 className="mt-4 text-4xl font-semibold">{i.headline?.title||"Your trading intelligence is ready."}</h2><p className="mt-3 text-slate-400">{i.headline?.message||"Performance analysis is active."}</p></section><section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{[["Net Profit",<Money v={s.net_profit}/>],["Win Rate",`${s.win_rate||0}%`],["Profit Factor",s.profit_factor||0],["Trader DNA",`${i.scorecard?.overall||0}/100`]].map(([a,b])=><div key={String(a)} className="premium-card rounded-3xl p-5"><p className="text-sm text-slate-500">{a}</p><p className="mt-3 text-3xl font-semibold">{b}</p></div>)}</section><div className="premium-card rounded-[2rem] p-6"><h3 className="text-xl font-semibold">Equity curve</h3><div className="mt-5 h-80">{eq.length?<ResponsiveContainer width="100%" height="100%"><AreaChart data={eq}><CartesianGrid stroke="rgba(148,163,184,.08)"/><XAxis dataKey="date"/><YAxis/><Tooltip/><Area type="monotone" dataKey="balance" stroke="#6d8dff" fill="#4f7cff33"/></AreaChart></ResponsiveContainer>:<div className="grid h-full place-items-center text-slate-500">No equity data yet</div>}</div></div></div>}
const empty={broker:"Manual",ticket:"",pair:"XAUUSD",direction:"BUY" as "BUY"|"SELL",entry:"",exit_price:"",stop_loss:"",take_profit:"",lot_size:"",profit:"",strategy:"",emotion:"",notes:""}
export function Trades(){const qc=useQueryClient(),q=useQuery({queryKey:["trades"],queryFn:trades});const [search,setSearch]=useState(""),[open,setOpen]=useState(false),[editing,setEditing]=useState<Trade|null>(null),[form,setForm]=useState(empty),[review,setReview]=useState<any>(null);const add=useMutation({mutationFn:addTrade,onSuccess:()=>{qc.invalidateQueries({queryKey:["trades"]});setOpen(false)}}),edit=useMutation({mutationFn:({id,p}:{id:number;p:Partial<TradePayload>})=>editTrade(id,p),onSuccess:()=>{qc.invalidateQueries({queryKey:["trades"]});setOpen(false)}}),del=useMutation({mutationFn:removeTrade,onSuccess:()=>qc.invalidateQueries({queryKey:["trades"]})});const all=q.data?.trades||[],filtered=useMemo(()=>all.filter(t=>[t.pair,t.strategy,t.broker,t.ticket].filter(Boolean).some(v=>String(v).toLowerCase().includes(search.toLowerCase()))),[all,search]);function oe(t:Trade){setEditing(t);setForm({broker:t.broker||"",ticket:t.ticket||"",pair:t.pair,direction:t.direction,entry:String(t.entry),exit_price:String(t.exit_price??""),stop_loss:String(t.stop_loss),take_profit:String(t.take_profit),lot_size:String(t.lot_size??""),profit:String(t.profit??""),strategy:t.strategy||"",emotion:t.emotion||"",notes:t.notes||""});setOpen(true)}async function sub(e:FormEvent){e.preventDefault();const p:TradePayload={broker:form.broker||null,ticket:form.ticket||null,pair:form.pair,direction:form.direction,entry:Number(form.entry),exit_price:form.exit_price?Number(form.exit_price):null,stop_loss:Number(form.stop_loss),take_profit:Number(form.take_profit),lot_size:form.lot_size?Number(form.lot_size):null,profit:form.profit?Number(form.profit):null,commission:0,swap:0,strategy:form.strategy||null,emotion:form.emotion||null,notes:form.notes||null,imported:false};editing?await edit.mutateAsync({id:editing.id,p}):await add.mutateAsync(p)}return <div className="space-y-6"><section className="premium-card grid-surface rounded-[2rem] p-8"><div className="flex justify-between"><div><p className="text-xs uppercase tracking-[.25em] text-blue-300">Trade journal</p><h2 className="mt-4 text-4xl font-semibold">Every trade becomes intelligence.</h2></div><button onClick={()=>{setEditing(null);setForm(empty);setOpen(true)}} className="flex h-fit items-center gap-2 rounded-2xl bg-blue-500 px-5 py-3 font-semibold"><Plus className="size-4"/>Add trade</button></div></section><div className="premium-card flex items-center gap-3 rounded-3xl px-4"><Search className="size-4"/><input value={search} onChange={e=>setSearch(e.target.value)} className="w-full bg-transparent py-3 outline-none" placeholder="Search trades..."/></div><div className="premium-card overflow-x-auto rounded-[2rem]"><table className="w-full min-w-[900px]"><thead><tr>{["Market","Direction","Entry","Exit","Profit","Strategy","Actions"].map(x=><th key={x} className="px-5 py-4 text-left text-xs uppercase text-slate-500">{x}</th>)}</tr></thead><tbody>{filtered.map(t=><tr key={t.id} className="border-t border-white/[.06]"><td className="px-5 py-4"><b>{t.pair}</b><div className="text-xs text-slate-500">{t.broker||"Manual"}</div></td><td className={`px-5 py-4 ${t.direction==="BUY"?"text-emerald-300":"text-red-300"}`}>{t.direction}</td><td className="px-5 py-4">{t.entry}</td><td className="px-5 py-4">{t.exit_price??"â€”"}</td><td className={`px-5 py-4 ${(t.profit||0)>=0?"text-emerald-300":"text-red-300"}`}>{t.profit??0}</td><td className="px-5 py-4">{t.strategy||"Unspecified"}</td><td className="px-5 py-4"><div className="flex gap-2"><button onClick={async()=>setReview({trade:t,data:await reviewTrade(t.id)})} className="rounded-xl bg-blue-400/10 p-2"><BrainCircuit className="size-4"/></button><button onClick={()=>oe(t)} className="rounded-xl bg-white/[.04] p-2"><Pencil className="size-4"/></button><button onClick={()=>confirm("Delete trade?")&&del.mutate(t.id)} className="rounded-xl bg-red-400/10 p-2 text-red-300"><Trash2 className="size-4"/></button></div></td></tr>)}</tbody></table></div>{open&&<div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><form onSubmit={sub} className="premium-card max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] p-7"><h3 className="text-2xl font-semibold">{editing?"Edit trade":"Add trade"}</h3><div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">{(["pair","broker","ticket"] as const).map(k=><input key={k} placeholder={k} className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>) }<select className="rounded-2xl bg-[#0b1120] px-4 py-3" value={form.direction} onChange={e=>setForm({...form,direction:e.target.value as any})}><option>BUY</option><option>SELL</option></select></div><div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-5">{(["entry","exit_price","stop_loss","take_profit","lot_size"] as const).map(k=><input key={k} type="number" step="any" placeholder={k} className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>)}</div><div className="mt-4 grid gap-4 md:grid-cols-3">{(["profit","strategy","emotion"] as const).map(k=><input key={k} placeholder={k} className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>)}</div><textarea className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" rows={4} placeholder="Notes" value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})}/><div className="mt-5 flex justify-end gap-3"><button type="button" onClick={()=>setOpen(false)} className="rounded-2xl border border-white/10 px-5 py-3">Cancel</button><button className="rounded-2xl bg-blue-500 px-5 py-3">Save</button></div></form></div>}{review&&<div className="fixed inset-0 z-50 flex justify-end bg-black/60"><aside className="h-full w-full max-w-xl overflow-y-auto bg-[#090f1c] p-8"><button onClick={()=>setReview(null)} className="float-right">Close</button><h3 className="text-2xl font-semibold">AI Review Â· {review.trade.pair}</h3><div className="mt-6 premium-card rounded-3xl p-5"><div className="text-4xl text-blue-300">{review.data.trade_score}</div><p className="mt-2">{review.data.summary}</p></div><h4 className="mt-6 text-emerald-300">Strengths</h4>{review.data.strengths?.map((x:string)=><p key={x} className="mt-2 rounded-2xl bg-emerald-400/[.05] p-3">{x}</p>)}<h4 className="mt-6 text-red-300">Mistakes</h4>{review.data.mistakes?.map((x:string)=><p key={x} className="mt-2 rounded-2xl bg-red-400/[.05] p-3">{x}</p>)}</aside></div>}</div>}
export function Analytics(){const q=useQuery({queryKey:["analysis"],queryFn:analysis});const d=q.data||{},p=d.performance||{},r=d.risk||{},ps=d.psychology||{},c=d.consistency?.score||{};return <Page title="Analytics" subtitle="Know exactly what drives your results."><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{[["Win Rate",`${p.win_rate||0}%`],["Profit Factor",p.profit_factor||0],["Expectancy",r.expectancy||0],["Max Drawdown",`${r.maximum_drawdown||0}%`],["Discipline",ps.discipline_score||0],["Consistency",c.overall_score||0]].map(([a,b])=><div key={String(a)} className="premium-card rounded-3xl p-6"><p className="text-slate-500">{a}</p><p className="mt-3 text-3xl font-semibold">{String(b)}</p></div>)}</div></Page>}
export function DNA(){const q=useQuery({queryKey:["analysis"],queryFn:analysis});const d=q.data?.trader_dna||{};return <Page title="Trader DNA" subtitle={d.profile||"Developing Trader"}><div className="grid gap-6 lg:grid-cols-2"><List title="Strengths" items={d.strengths||[]} good/><List title="Weaknesses" items={d.weaknesses||[]}/></div></Page>}
function List({title,items,good}:{title:string;items:string[];good?:boolean}){return <div className="premium-card rounded-3xl p-6"><h3 className={`text-xl ${good?"text-emerald-300":"text-red-300"}`}>{title}</h3>{items.map(x=><div key={x} className="mt-3 rounded-2xl bg-white/[.03] p-4">{x}</div>)}</div>}
export function Coach(){const [msgs,setMsgs]=useState<any[]>([{role:"assistant",text:"Ask me about your performance, psychology or priorities."}]),[text,setText]=useState("");async function sub(e:FormEvent){e.preventDefault();if(!text)return;const t=text;setMsgs(m=>[...m,{role:"user",text:t}]);setText("");try{const r=await coach(t);setMsgs(m=>[...m,{role:"assistant",text:r.answer||"Analysis complete."}])}catch{setMsgs(m=>[...m,{role:"assistant",text:"AI service unavailable; local fallback remains active."}])}}return <div className="premium-card flex min-h-[72vh] flex-col rounded-[2rem] p-6"><h2 className="text-3xl font-semibold">AI Coach</h2><div className="mt-6 flex-1 space-y-4">{msgs.map((m,i)=><div key={i} className={`max-w-[80%] rounded-3xl p-4 ${m.role==="user"?"ml-auto bg-blue-500":"bg-white/[.05]"}`}>{m.text}</div>)}</div><form onSubmit={sub} className="mt-5 flex gap-3"><input className="flex-1 rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" value={text} onChange={e=>setText(e.target.value)} placeholder="Why am I losing?"/><button className="rounded-2xl bg-blue-500 px-5">Send</button></form></div>}
export function Reports(){const w=useQuery({queryKey:["weekly"],queryFn:weekly}),m=useQuery({queryKey:["monthly"],queryFn:monthly});return <Page title="Reports" subtitle="Weekly and monthly performance reviews."><div className="grid gap-6 lg:grid-cols-2">{[["Weekly",w.data],["Monthly",m.data]].map(([t,d]:any)=><div key={t} className="premium-card rounded-3xl p-6"><p className="text-blue-300">{t} review</p><p className="mt-4 text-4xl font-semibold">{d?.grade||"â€”"}</p><p className="mt-2 text-slate-400">Score {d?.score||0}/100</p><p className="mt-5">{d?.summary||"No report yet."}</p></div>)}</div></Page>}
export function Strategy(){const [saved,setSaved]=useState(false);return <Page title="Strategy Lab" subtitle="Teach TradePilot AI exactly how you trade."><div className="grid gap-6 xl:grid-cols-[1.2fr_.8fr]"><div className="premium-card rounded-3xl p-6"><input className="w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" defaultValue="London Breakout"/><textarea className="mt-4 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3" rows={10} defaultValue={`Trade London session only
Wait for liquidity sweep
Require structure shift
Risk maximum 0.5%`}/><div className="mt-4 rounded-2xl border border-dashed border-white/10 p-8 text-center"><Upload className="mx-auto"/><p className="mt-3">Upload charts, PDFs or notes</p><input type="file" multiple className="mt-4"/></div><button onClick={()=>setSaved(true)} className="mt-4 rounded-2xl bg-blue-500 px-5 py-3">Save strategy</button></div><div className="premium-card rounded-3xl p-6"><h3 className="text-xl font-semibold">Approval-based automation</h3><p className="mt-3 text-slate-400">AI prepares a setup against your rules. You approve before execution. Unattended trading stays disabled until broker and risk controls are validated.</p>{saved&&<div className="mt-5 rounded-2xl bg-emerald-400/10 p-4 text-emerald-300">Strategy profile saved locally.</div>}</div></div></Page>}
export function LegacyPartnersOld(){const offers=[["Recommended Broker","MT5 Â· tracked minimum deposit"],["Prop Firm Challenge","Evaluation and partner signup"],["Lloyd Traders LTD","Trading signals coming soon"],["Affiliate Marketplace","Books, tools and education"]];return <Page title="Brokers & Partners" subtitle="Recommended brokers, prop firms and partner resources."><div className="grid gap-5 md:grid-cols-2">{offers.map(([n,d])=><div key={n} className="premium-card rounded-3xl p-6"><h3 className="text-xl font-semibold">{n}</h3><p className="mt-3 text-slate-400">{d}</p><button className="mt-5 flex items-center gap-2 rounded-2xl border border-white/10 px-4 py-2"><ExternalLink className="size-4"/>View offer</button></div>)}</div><div className="mt-6 rounded-3xl bg-amber-400/[.05] p-5 text-sm text-slate-400">Affiliate disclosure: TradePilot AI may earn commissions through partner links. Trading involves risk.</div></Page>}
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
    },
    {
      name:"Pro",
      code:"pro",
      launchPrice:"$10",
      normalPrice:"$19.99/month",
      detail:"First month",
    },
    {
      name:"Premium",
      code:"premium",
      launchPrice:"$10",
      normalPrice:"$29.99/month",
      detail:"First month",
    },
  ] as const

  return (
    <Page
      title="Billing"
      subtitle="Flexible plans for every stage of your trading journey."
    >
      {subscription && (
        <div className="premium-card rounded-3xl p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-500">
                Current subscription
              </p>

              <p className="mt-1 text-xl font-semibold capitalize">
                {subscription.plan}
              </p>

              <p className="mt-1 text-sm text-slate-400">
                Status:{" "}
                <span className="capitalize">
                  {subscription.status}
                </span>
              </p>

              {subscription.next_billing_at && (
                <p className="mt-1 text-sm text-slate-400">
                  Next billing:{" "}
                  {new Date(
                    subscription.next_billing_at
                  ).toLocaleDateString()}
                </p>
              )}
            </div>

            {subscription.plan!=="free" &&
             subscription.status!=="cancelled" &&
             subscription.status!=="canceled" && (
              <button
                type="button"
                onClick={cancelPlan}
                className="rounded-2xl border border-red-400/30 px-5 py-3 text-red-300 hover:bg-red-400/10"
              >
                Cancel anytime
              </button>
            )}
          </div>
        </div>
      )}

      {message && (
        <div className="rounded-2xl border border-blue-400/20 bg-blue-400/10 p-4 text-sm text-blue-200">
          {message}
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-3">
        {plans.map(plan=>(
          <div
            key={plan.code}
            className="premium-card rounded-3xl p-6"
          >
            <h3 className="text-xl font-semibold">
              {plan.name}
            </h3>

            {plan.code!=="free" && (
              <div className="mt-4 inline-flex rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-300">
                Launch Offer
              </div>
            )}

            <p className="mt-4 text-4xl font-semibold">
              {plan.launchPrice}
            </p>

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

            {plan.code!=="free" && (
              <p className="mt-2 text-xs text-slate-500">
                Cancel anytime
              </p>
            )}

            <p className="mt-5 text-sm text-slate-400">
              Preferred display currency:{" "}
              <span className="font-medium text-slate-200">
                {user?.preferred_currency || "USD"}
              </span>
            </p>

            {plan.code==="free" ? (
              <button
                type="button"
                disabled
                className="mt-6 w-full rounded-2xl bg-white/5 py-3 text-slate-500"
              >
                Free plan
              </button>
            ) : (
              <button
                type="button"
                disabled={
                  busyPlan!=="" ||
                  subscription?.status==="active"
                }
                onClick={()=>
                  choosePlan(plan.code)
                }
                className="mt-6 w-full rounded-2xl bg-blue-500 py-3 font-medium disabled:opacity-50"
              >
                {busyPlan===plan.code
                  ? "Opening PayPal..."
                  : `Choose ${plan.name}`}
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="premium-card rounded-3xl p-5 text-sm text-slate-400">
        <p>
          PayPal billing currency: USD.
        </p>

        <p className="mt-2">
          Pro: $10 for the first month, then $19.99/month.
        </p>

        <p className="mt-1">
          Premium: $10 for the first month, then $29.99/month.
        </p>

        <p className="mt-1">
          Cancel anytime to stop future renewals.
        </p>
      </div>
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
      <div className="premium-card max-w-3xl rounded-3xl p-6">
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
          className="mt-6 rounded-2xl bg-blue-500 px-6 py-3 font-medium disabled:opacity-50"
        >
          {saving
            ? "Saving..."
            : t("savePreferences")}
        </button>
      </div>
    </Page>
  )
}
function Page({title,subtitle,children}:{title:string;subtitle:string;children:any}){return <div className="space-y-6"><section className="premium-card grid-surface rounded-[2rem] p-8"><p className="text-xs uppercase tracking-[.25em] text-blue-300">TradePilot AI</p><h2 className="mt-4 text-4xl font-semibold">{title}</h2><p className="mt-3 text-slate-400">{subtitle}</p></section>{children}</div>}
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
