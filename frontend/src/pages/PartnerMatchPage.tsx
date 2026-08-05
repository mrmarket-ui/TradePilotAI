import {useMemo,useState} from "react"
import {useQuery} from "@tanstack/react-query"
import {BrainCircuit,CheckCircle2} from "lucide-react"

import {getPartners,type Partner} from "@/api/partners"

export default function PartnerMatchPage(){
  const q=useQuery({
    queryKey:["partners"],
    queryFn:()=>getPartners(),
  })

  const [capital,setCapital]=useState("500")
  const [goal,setGoal]=useState<"broker"|"prop_firm">("broker")
  const [platform,setPlatform]=useState("MT5")

  const matches=useMemo(()=>{
    const list=(q.data||[]).filter(p=>p.category===goal)

    return list
      .map((p:Partner)=>{
        let score=50

        if(p.featured) score+=15

        if(
          platform &&
          p.platforms?.some(x=>x.toLowerCase()===platform.toLowerCase())
        ){
          score+=20
        }

        if(goal==="prop_firm"&&p.challenge_size){
          score+=10
        }

        if(goal==="broker"&&p.minimum_deposit){
          score+=10
        }

        return {
          partner:p,
          score:Math.min(score,100),
        }
      })
      .sort((a,b)=>b.score-a.score)
  },[q.data,goal,platform])

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[.25em] text-blue-300">
          Smart Match
        </p>
        <h1 className="mt-2 text-3xl font-semibold">
          Find a Partner That Fits You
        </h1>
      </header>

      <section className="premium-card grid gap-4 rounded-3xl p-6 md:grid-cols-3">
        <input
          value={capital}
          onChange={e=>setCapital(e.target.value)}
          placeholder="Capital"
          className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3"
        />

        <select
          value={goal}
          onChange={e=>setGoal(e.target.value as any)}
          className="rounded-2xl bg-[#0b1120] px-4 py-3"
        >
          <option value="broker">Find Broker</option>
          <option value="prop_firm">Find Prop Firm</option>
        </select>

        <select
          value={platform}
          onChange={e=>setPlatform(e.target.value)}
          className="rounded-2xl bg-[#0b1120] px-4 py-3"
        >
          <option>MT5</option>
          <option>MT4</option>
          <option>Web</option>
        </select>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {matches.slice(0,3).map(({partner,score})=>(
          <div key={partner.id} className="premium-card rounded-3xl p-6">
            <div className="flex items-center justify-between">
              <BrainCircuit className="size-5 text-blue-300"/>
              <span className="text-sm text-slate-400">{score}% match</span>
            </div>

            <h3 className="mt-4 text-xl font-semibold">{partner.name}</h3>

            <p className="mt-3 text-sm text-slate-400">
              {partner.description}
            </p>

            <div className="mt-5 space-y-2 text-sm">
              <p className="flex items-center gap-2">
                <CheckCircle2 className="size-4 text-emerald-300"/>
                Fits selected partner type
              </p>

              {partner.featured&&(
                <p className="flex items-center gap-2">
                  <CheckCircle2 className="size-4 text-emerald-300"/>
                  Featured by TradePilot AI
                </p>
              )}
            </div>
          </div>
        ))}
      </section>

      <p className="text-xs text-slate-500">
        Match scores are based only on partner information stored in TradePilot AI and are not financial advice.
      </p>
    </div>
  )
}
