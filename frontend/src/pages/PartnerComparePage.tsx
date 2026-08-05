import {useMemo,useState} from "react"
import {useQuery} from "@tanstack/react-query"
import {ArrowLeftRight,Star} from "lucide-react"

import {getPartners,type Partner} from "@/api/partners"

export default function PartnerComparePage(){
  const q=useQuery({
    queryKey:["partners"],
    queryFn:()=>getPartners(),
  })

  const [leftId,setLeftId]=useState<number|null>(null)
  const [rightId,setRightId]=useState<number|null>(null)

  const partners=q.data||[]

  const left=useMemo(
    ()=>partners.find(p=>p.id===leftId)||null,
    [partners,leftId],
  )

  const right=useMemo(
    ()=>partners.find(p=>p.id===rightId)||null,
    [partners,rightId],
  )

  const rows=[
    ["Category",(p:Partner)=>p.category.replace("_"," ")],
    ["Minimum Deposit",(p:Partner)=>p.minimum_deposit||"Check provider"],
    ["Platforms",(p:Partner)=>p.platforms?.join(", ")||"Check provider"],
    ["Regulation",(p:Partner)=>p.regulation||"Check provider"],
    ["Challenge Size",(p:Partner)=>p.challenge_size||"N/A"],
    ["Challenge Fee",(p:Partner)=>p.challenge_fee||"N/A"],
    ["Profit Split",(p:Partner)=>p.profit_split||"N/A"],
    ["Max Drawdown",(p:Partner)=>p.max_drawdown||"N/A"],
    ["Payout Frequency",(p:Partner)=>p.payout_frequency||"Check provider"],
  ] as const

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[.25em] text-blue-300">
          Partner Comparison
        </p>
        <h1 className="mt-2 text-3xl font-semibold">
          Compare Brokers & Prop Firms
        </h1>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        <select
          value={leftId||""}
          onChange={e=>setLeftId(Number(e.target.value)||null)}
          className="rounded-2xl bg-[#0b1120] px-4 py-3"
        >
          <option value="">Choose first partner</option>
          {partners.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}
        </select>

        <select
          value={rightId||""}
          onChange={e=>setRightId(Number(e.target.value)||null)}
          className="rounded-2xl bg-[#0b1120] px-4 py-3"
        >
          <option value="">Choose second partner</option>
          {partners.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>

      {left&&right&&(
        <div className="premium-card overflow-x-auto rounded-3xl">
          <table className="w-full min-w-[750px]">
            <thead>
              <tr>
                <th className="px-5 py-4 text-left text-slate-500">Feature</th>
                <th className="px-5 py-4 text-left">{left.name}</th>
                <th className="px-5 py-4 text-left">{right.name}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(([label,getValue])=>(
                <tr key={label} className="border-t border-white/[.06]">
                  <td className="px-5 py-4 text-slate-500">{label}</td>
                  <td className="px-5 py-4">{getValue(left)}</td>
                  <td className="px-5 py-4">{getValue(right)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!left||!right?(
        <div className="premium-card rounded-3xl p-8 text-center text-slate-400">
          <ArrowLeftRight className="mx-auto mb-3 size-6"/>
          Choose two partners to compare.
        </div>
      ):null}
    </div>
  )
}
