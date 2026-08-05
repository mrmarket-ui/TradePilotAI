import {
  ArrowLeft,
  ExternalLink,
  ShieldCheck,
  Star,
} from "lucide-react"
import {
  useNavigate,
  useParams,
} from "react-router-dom"
import {useQuery} from "@tanstack/react-query"

import {api} from "@/api"
import type {Partner} from "@/api/partners"
import {trackPartnerClick} from "@/api/partners"

const getPartner=async(slug:string)=>
  (
    await api.get<Partner>(
      `/partners/${slug}`,
    )
  ).data

export default function PartnerDetailPage(){
  const {slug=""}=useParams()
  const nav=useNavigate()

  const q=useQuery({
    queryKey:["partner",slug],
    queryFn:()=>getPartner(slug),
    enabled:Boolean(slug),
  })

  if(q.isLoading){
    return <p className="p-8 text-slate-400">Loading partner...</p>
  }

  if(!q.data){
    return <p className="p-8 text-red-300">Partner not found.</p>
  }

  const p=q.data

  async function openPartner(){
    try{
      const result=await trackPartnerClick(
        p.id,
        "partner_detail",
      )

      window.open(
        result.redirect_url || p.referral_url,
        "_blank",
        "noopener,noreferrer",
      )
    }catch{
      window.open(
        p.referral_url,
        "_blank",
        "noopener,noreferrer",
      )
    }
  }

  return (
    <div className="space-y-6">
      <button
        onClick={()=>nav(-1)}
        className="flex items-center gap-2 text-sm text-slate-400"
      >
        <ArrowLeft className="size-4"/>
        Back
      </button>

      <section className="premium-card rounded-[2rem] p-8">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <div className="flex flex-wrap gap-2">
              <span className="rounded-full bg-blue-400/10 px-3 py-1 text-xs text-blue-300">
                {p.badge || p.category.replace("_"," ")}
              </span>

              {p.featured && (
                <span className="flex items-center gap-1 rounded-full bg-amber-400/10 px-3 py-1 text-xs text-amber-300">
                  <Star className="size-3"/>
                  Featured
                </span>
              )}
            </div>

            <h1 className="mt-5 text-4xl font-semibold">
              {p.name}
            </h1>

            <p className="mt-4 max-w-3xl leading-7 text-slate-400">
              {p.description}
            </p>
          </div>

          <button
            onClick={openPartner}
            className="flex items-center gap-2 rounded-2xl bg-blue-500 px-5 py-3 font-medium"
          >
            Visit Partner
            <ExternalLink className="size-4"/>
          </button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {[
          ["Minimum Deposit",p.minimum_deposit],
          ["Platforms",p.platforms?.join(", ")],
          ["Regulation",p.regulation],
          ["Challenge Size",p.challenge_size],
          ["Challenge Fee",p.challenge_fee],
          ["Profit Split",p.profit_split],
          ["Max Drawdown",p.max_drawdown],
          ["Payout Frequency",p.payout_frequency],
        ]
          .filter(([,value])=>Boolean(value))
          .map(([label,value])=>(
            <div
              key={label}
              className="premium-card rounded-3xl p-5"
            >
              <p className="text-sm text-slate-500">{label}</p>
              <p className="mt-2 text-lg font-medium">{value}</p>
            </div>
          ))}
      </section>

      <section className="rounded-3xl border border-amber-400/20 bg-amber-400/[.05] p-5 text-sm leading-6 text-slate-400">
        <div className="flex gap-3">
          <ShieldCheck className="mt-1 size-5 shrink-0 text-amber-300"/>
          <p>
            TradePilot AI does not operate this third-party provider.
            Terms, pricing, eligibility, withdrawals and trading rules are
            determined by the provider. Review their official terms before
            opening an account or purchasing a challenge.
          </p>
        </div>
      </section>
    </div>
  )
}
