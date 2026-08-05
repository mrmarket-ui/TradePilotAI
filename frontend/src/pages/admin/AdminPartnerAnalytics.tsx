import {useQuery} from "@tanstack/react-query"
import {useState} from "react"
import {
  BarChart3,
  MousePointerClick,
  Bookmark,
  Trophy,
} from "lucide-react"

import {getAdminPartnerAnalytics} from "@/api/admin/partners"

export default function AdminPartnerAnalytics(){
  const [days,setDays]=useState(30)

  const q=useQuery({
    queryKey:["admin-partners-analytics",days],
    queryFn:()=>getAdminPartnerAnalytics(days),
  })

  const d=q.data

  if(q.isLoading){
    return <p className="text-slate-400">Loading analytics...</p>
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[.25em] text-blue-300">
          Affiliate Analytics
        </p>
        <h1 className="mt-2 text-3xl font-semibold">
          Partner Performance
        </h1>
        <div className="mt-4 flex gap-2">
          {[7,30,90].map(value=>(
            <button
              key={value}
              onClick={()=>setDays(value)}
              className={`rounded-xl px-4 py-2 text-sm ${
                days===value
                  ?"bg-blue-500"
                  :"border border-white/10"
              }`}
            >
              {value} days
            </button>
          ))}
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        {[
          ["Total Clicks",d?.total_clicks||0,MousePointerClick],
          ["Partners",d?.total_partners||0,BarChart3],
          ["Active",d?.active_partners||0,Trophy],
          ["Saved",d?.saved_count||0,Bookmark],
        ].map(([label,value,Icon]:any)=>(
          <div key={label} className="premium-card rounded-3xl p-5">
            <Icon className="size-5 text-blue-300"/>
            <p className="mt-4 text-sm text-slate-500">{label}</p>
            <p className="mt-2 text-3xl font-semibold">{value}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="premium-card rounded-3xl p-6">
          <h2 className="text-xl font-semibold">Most Popular Partners</h2>

          <div className="mt-5 space-y-3">
            {(d?.partners||[]).map((item,index)=>(
              <div
                key={item.partner_id}
                className="flex items-center justify-between rounded-2xl bg-white/[.03] p-4"
              >
                <div>
                  <p className="font-medium">
                    #{index+1} {item.name}
                  </p>
                  <p className="text-xs capitalize text-slate-500">
                    {item.category.replace("_"," ")}
                  </p>
                </div>

                <div className="text-right">
                  <p className="text-lg font-semibold">{item.clicks}</p>
                  <p className="text-xs text-slate-500">clicks</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="premium-card rounded-3xl p-6">
          <h2 className="text-xl font-semibold">Traffic Sources</h2>

          <div className="mt-5 space-y-3">
            {(d?.sources||[]).map(item=>(
              <div
                key={item.source}
                className="flex items-center justify-between rounded-2xl bg-white/[.03] p-4"
              >
                <p className="capitalize">
                  {item.source.replaceAll("_"," ")}
                </p>

                <p className="font-semibold">
                  {item.clicks}
                </p>
              </div>
            ))}

            {!d?.sources?.length&&(
              <p className="text-sm text-slate-500">
                No tracked traffic yet.
              </p>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}

