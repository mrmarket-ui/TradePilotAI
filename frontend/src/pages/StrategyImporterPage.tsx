import {
  FileText,
  Image,
  Link,
  Loader2,
  Save,
  Sparkles,
  Upload,
  Video,
} from "lucide-react"
import {useState} from "react"
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"
import {useNavigate} from "react-router-dom"

import {
  addStrategyUrl,
  analyzeStrategySource,
  getStrategySources,
  saveImportedStrategy,
  uploadStrategySource,
  type StrategySource,
} from "@/api/strategySources"


export default function StrategyImporterPage(){
  const qc=useQueryClient()
  const nav=useNavigate()

  const [url,setUrl]=useState("")
  const [message,setMessage]=useState("")

  const q=useQuery({
    queryKey:["strategy-sources"],
    queryFn:getStrategySources,
  })

  const upload=useMutation({
    mutationFn:uploadStrategySource,
    onSuccess:async()=>{
      await qc.invalidateQueries({
        queryKey:["strategy-sources"],
      })
      setMessage(
        "Source uploaded successfully.",
      )
    },
  })

  const addUrl=useMutation({
    mutationFn:addStrategyUrl,
    onSuccess:async()=>{
      setUrl("")
      await qc.invalidateQueries({
        queryKey:["strategy-sources"],
      })
    },
  })

  const analyze=useMutation({
    mutationFn:analyzeStrategySource,
    onSuccess:async()=>{
      await qc.invalidateQueries({
        queryKey:["strategy-sources"],
      })
      setMessage(
        "AI strategy analysis completed.",
      )
    },
  })

  const save=useMutation({
    mutationFn:saveImportedStrategy,
    onSuccess:data=>{
      setMessage(
        `Strategy "${data.name}" saved.`,
      )

      setTimeout(()=>{
        nav("/strategy-lab")
      },700)
    },
  })

  function iconFor(source:StrategySource){
    if(source.source_type==="pdf")
      return FileText

    if(source.source_type==="image")
      return Image

    if(source.source_type==="video")
      return Video

    if(source.source_type==="url")
      return Link

    return FileText
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[.25em] text-blue-300">
          AI Strategy Importer
        </p>

        <h1 className="mt-3 text-3xl font-semibold">
          Teach TradePilot AI Your Strategy
        </h1>

        <p className="mt-3 max-w-3xl text-slate-400">
          Upload a PDF, chart screenshot,
          strategy image, notes or link.
          TradePilot AI extracts the trading
          rules and converts them into a
          structured Strategy Lab profile.
        </p>
      </header>

      {message&&(
        <div className="rounded-2xl border border-blue-400/20 bg-blue-400/[.07] p-4 text-blue-200">
          {message}
        </div>
      )}

      <section className="grid gap-5 lg:grid-cols-2">
        <label className="premium-card cursor-pointer rounded-3xl p-7">
          <Upload className="size-7 text-blue-300"/>

          <h2 className="mt-4 text-xl font-semibold">
            Upload Strategy
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            PDF, TXT, Markdown, PNG, JPG,
            WEBP or video.
          </p>

          <input
            type="file"
            className="mt-5 block w-full text-sm"
            accept=".pdf,.txt,.md,.png,.jpg,.jpeg,.webp,.mp4,.mov,.m4v"
            onChange={e=>{
              const file=e.target.files?.[0]

              if(file){
                upload.mutate(file)
              }
            }}
          />

          {upload.isPending&&(
            <p className="mt-4 flex items-center gap-2 text-sm text-blue-300">
              <Loader2 className="size-4 animate-spin"/>
              Uploading...
            </p>
          )}
        </label>

        <section className="premium-card rounded-3xl p-7">
          <Link className="size-7 text-emerald-300"/>

          <h2 className="mt-4 text-xl font-semibold">
            Import From Link
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Paste a strategy article,
            educational page or trading-plan
            link.
          </p>

          <input
            value={url}
            onChange={e=>setUrl(e.target.value)}
            placeholder="https://..."
            className="mt-5 w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3 outline-none"
          />

          <button
            onClick={()=>addUrl.mutate(url)}
            disabled={!url||addUrl.isPending}
            className="mt-3 rounded-2xl bg-emerald-500 px-5 py-3 font-medium disabled:opacity-50"
          >
            Add Link
          </button>
        </section>
      </section>

      <section>
        <h2 className="text-2xl font-semibold">
          Strategy Sources
        </h2>

        <div className="mt-5 space-y-4">
          {(q.data||[]).map(source=>{
            const Icon=iconFor(source)

            return (
              <article
                key={source.id}
                className="premium-card rounded-3xl p-6"
              >
                <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
                  <div className="flex gap-4">
                    <div className="grid size-12 place-items-center rounded-2xl bg-blue-500/10">
                      <Icon className="size-5 text-blue-300"/>
                    </div>

                    <div>
                      <h3 className="font-semibold">
                        {source.original_name||
                          source.source_url||
                          `Source #${source.id}`}
                      </h3>

                      <p className="mt-1 text-sm capitalize text-slate-500">
                        {source.source_type}
                        {" · "}
                        {source.status}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {source.source_type!=="video"&&(
                      <button
                        onClick={()=>
                          analyze.mutate(source.id)
                        }
                        disabled={analyze.isPending}
                        className="flex items-center gap-2 rounded-2xl bg-blue-500 px-4 py-2 text-sm"
                      >
                        <Sparkles className="size-4"/>
                        Analyze
                      </button>
                    )}

                    {source.extracted_strategy&&(
                      <button
                        onClick={()=>
                          save.mutate(source.id)
                        }
                        className="flex items-center gap-2 rounded-2xl border border-white/10 px-4 py-2 text-sm"
                      >
                        <Save className="size-4"/>
                        Save to Strategy Lab
                      </button>
                    )}
                  </div>
                </div>

                {source.extracted_strategy&&(
                  <div className="mt-5 rounded-2xl bg-white/[.03] p-5">
                    <h4 className="font-semibold text-emerald-300">
                      AI Extracted Strategy
                    </h4>

                    <p className="mt-3">
                      {String(
                        source.extracted_strategy.name||
                        "Imported Strategy",
                      )}
                    </p>

                    <p className="mt-2 text-sm text-slate-400">
                      {
                        (
                          source.extracted_strategy.entry_rules||
                          []
                        ).length
                      } entry rules ·{" "}
                      {
                        (
                          source.extracted_strategy.confirmations||
                          []
                        ).length
                      } confirmations ·{" "}
                      {
                        (
                          source.extracted_strategy.exit_rules||
                          []
                        ).length
                      } exit rules
                    </p>
                  </div>
                )}
              </article>
            )
          })}
        </div>
      </section>
    </div>
  )
}
