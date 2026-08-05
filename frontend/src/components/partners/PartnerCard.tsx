import {
  ArrowLeftRight,
  Bookmark,
  ExternalLink,
  Star,
} from "lucide-react"
import {useNavigate} from "react-router-dom"

import type {Partner} from "@/api/partners"

type Props={
  partner:Partner
  saved:boolean
  busy?:boolean
  onOpen:(partner:Partner)=>void
  onSave:(partner:Partner)=>void
}

export default function PartnerCard({
  partner,
  saved,
  busy=false,
  onOpen,
  onSave,
}:Props){
  const nav=useNavigate()

  const propFirm=
    partner.category==="prop_firm"

  return (
    <article className="premium-card flex h-full flex-col rounded-3xl p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-wrap gap-2">
          <span
            className={
              propFirm
                ?"rounded-full bg-blue-400/10 px-3 py-1 text-xs text-blue-300"
                :"rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300"
            }
          >
            {partner.badge||
              (propFirm
                ?"Prop Firm"
                :"Broker")}
          </span>

          {partner.featured&&(
            <span className="flex items-center gap-1 rounded-full bg-amber-400/10 px-3 py-1 text-xs text-amber-300">
              <Star className="size-3"/>
              Featured
            </span>
          )}
        </div>

        <button
          disabled={busy}
          onClick={()=>onSave(partner)}
          className="rounded-xl border border-white/10 p-2"
        >
          <Bookmark
            className={`size-5 ${
              saved
                ?"fill-current text-blue-300"
                :""
            }`}
          />
        </button>
      </div>

      <h3 className="mt-5 text-xl font-semibold">
        {partner.name}
      </h3>

      <p className="mt-3 flex-1 text-sm leading-6 text-slate-400">
        {partner.description}
      </p>

      <div className="mt-6 grid grid-cols-2 gap-2">
        <button
          onClick={()=>nav(
            `/partners/${partner.slug}`,
          )}
          className="rounded-2xl border border-white/10 px-3 py-3 text-sm"
        >
          Details
        </button>

        <button
          onClick={()=>nav(
            "/partners/compare",
          )}
          className="flex items-center justify-center gap-2 rounded-2xl border border-white/10 px-3 py-3 text-sm"
        >
          <ArrowLeftRight className="size-4"/>
          Compare
        </button>
      </div>

      <button
        onClick={()=>onOpen(partner)}
        className="mt-2 flex items-center justify-center gap-2 rounded-2xl bg-blue-500 px-4 py-3 font-medium"
      >
        {propFirm
          ?"View Opportunity"
          :"Visit Broker"}

        <ExternalLink className="size-4"/>
      </button>
    </article>
  )
}
