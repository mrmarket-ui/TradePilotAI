import { useState } from "react"
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  ImagePlus,
  Loader2,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  Upload,
  X,
} from "lucide-react"

import {
  analyzeGeneralMacroEvidence,
  type GeneralMacroAnalysisResponse,
} from "@/api/macroIntelligence"

type MacroEvent = "GENERAL" | "NFP" | "CPI" | "PPI" | "FOMC"

const supportedEvents: MacroEvent[] = [
  "GENERAL",
  "NFP",
  "CPI",
  "PPI",
  "FOMC",
]

function classificationDescription(
  classification: GeneralMacroAnalysisResponse["classification"],
) {
  switch (classification) {
    case "STRONG":
      return "Strong economic evidence detected."
    case "POSITIVE":
      return "The supplied evidence is broadly positive."
    case "MIXED":
      return "The evidence contains meaningful positive and negative factors."
    case "WEAK":
      return "The supplied evidence is broadly weak."
    default:
      return "There is not enough reliable evidence for a directional conclusion."
  }
}

function biasDescription(
  bias: GeneralMacroAnalysisResponse["usd_bias"],
) {
  switch (bias) {
    case "BULLISH":
      return "The combined economic evidence is supportive of USD strength."
    case "BEARISH":
      return "The combined economic evidence is supportive of USD weakness."
    case "MIXED":
      return "The economic evidence contains conflicting USD drivers."
    default:
      return "The supplied evidence does not establish a clear USD direction."
  }
}

function relevanceClass(
  relevance: GeneralMacroAnalysisResponse["extracted_indicators"][number]["relevance"],
) {
  switch (relevance) {
    case "HIGH":
      return "border-emerald-400/20 bg-emerald-400/[0.06] text-emerald-300"
    case "MEDIUM":
      return "border-blue-400/20 bg-blue-400/[0.06] text-blue-300"
    case "LOW":
      return "border-slate-400/15 bg-white/[0.03] text-slate-400"
    default:
      return "border-amber-400/20 bg-amber-400/[0.05] text-amber-300"
  }
}

function valueOrDash(value: string | null) {
  return value?.trim() ? value : "—"
}

export default function MacroIntelligencePage() {
  const [activeEvent, setActiveEvent] =
    useState<MacroEvent>("GENERAL")

  const [evidence, setEvidence] = useState("")
  const [images, setImages] = useState<File[]>([])
  const [analysis, setAnalysis] =
    useState<GeneralMacroAnalysisResponse | null>(null)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function runAnalysis() {
    if (!evidence.trim() && images.length === 0) {
      setError(
        "Add economic information, upload a screenshot, or provide both.",
      )
      return
    }

    setLoading(true)
    setError(null)
    setAnalysis(null)

    try {
      const result = await analyzeGeneralMacroEvidence(
        evidence,
        images,
      )

      setAnalysis(result)
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail

      setError(
        typeof detail === "string"
          ? detail
          : "The economic evidence could not be analysed. Please try again.",
      )
    } finally {
      setLoading(false)
    }
  }

  function addImages(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const selected = Array.from(
      event.target.files ?? [],
    )

    if (!selected.length) return

    setImages((current) =>
      [...current, ...selected].slice(0, 5),
    )

    event.target.value = ""
  }

  function removeImage(index: number) {
    setImages((current) =>
      current.filter((_, itemIndex) => itemIndex !== index),
    )
  }

  return (
    <div className="space-y-6 pb-10">
      <section className="premium-card rounded-[2rem] p-6 md:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">
              Macro Intelligence
            </p>

            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">
              General Economic Intelligence
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Submit economic information in whatever form you have it:
              paragraphs, calendar data, numbers, notes, or screenshots.
              TradePilot AI reads the complete submission before forming an
              economic assessment.
            </p>
          </div>

          <div className="rounded-2xl border border-blue-400/15 bg-blue-400/[0.04] px-4 py-3 text-xs text-slate-400">
            Decision-support only
          </div>
        </div>

        <div className="mt-7 flex flex-wrap gap-2">
          {supportedEvents.map((event) => {
            const active = event === activeEvent

            return (
              <button
                key={event}
                type="button"
                onClick={() => {
                  if (event === "GENERAL") {
                    setActiveEvent(event)
                    return
                  }

                  setActiveEvent(event)
                }}
                className={`rounded-xl border px-4 py-2 text-sm font-medium transition ${
                  active
                    ? "border-blue-400/30 bg-blue-400/10 text-blue-200"
                    : "border-white/[0.08] bg-white/[0.025] text-slate-500"
                }`}
              >
                {event === "GENERAL"
                  ? "General AI"
                  : `${event} Analyzer`}
              </button>
            )
          })}
        </div>

        {activeEvent !== "GENERAL" ? (
          <div className="mt-5 flex items-start gap-3 rounded-2xl border border-amber-400/15 bg-amber-400/[0.04] p-4">
            <Clock3 className="mt-0.5 size-5 shrink-0 text-amber-300" />

            <div>
              <p className="text-sm font-medium text-white">
                {activeEvent} Analyzer
              </p>

              <p className="mt-1 text-sm leading-6 text-slate-400">
                Event-specific {activeEvent} analysis is being expanded.
                The General AI engine is currently the active multi-indicator
                analyst.
              </p>
            </div>
          </div>
        ) : null}

        <div className="mt-6">
          <label
            htmlFor="macro-evidence"
            className="mb-2 block text-sm font-medium text-slate-300"
          >
            Economic evidence
          </label>

          <textarea
            id="macro-evidence"
            value={evidence}
            onChange={(event) =>
              setEvidence(event.target.value)
            }
            placeholder={`Paste anything you have here.

Example:
ISM Manufacturing PMI 54.6 vs forecast 55.2, previous 55.6.
ADP Non-Farm Employment 38K vs forecast 47K, previous 46K.
PPI m/m 1.6% vs forecast 1.2%, previous -0.3%.
Unemployment Claims 206K vs forecast 205K, previous 204K.

You do not need to format the information. TradePilot AI will read the submission as a whole.`}
            className="min-h-[220px] w-full resize-y rounded-2xl border border-white/[0.08] bg-black/20 px-4 py-4 text-sm leading-6 text-slate-200 outline-none placeholder:text-slate-600 focus:border-blue-400/30"
          />
        </div>

        <div className="mt-5 rounded-2xl border border-dashed border-white/[0.12] bg-white/[0.02] p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <ImagePlus className="mt-0.5 size-5 text-blue-300" />

              <div>
                <p className="text-sm font-medium text-white">
                  Add screenshots
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Upload up to 5 PNG, JPEG or WEBP screenshots.
                </p>
              </div>
            </div>

            <label className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 py-2.5 text-sm font-medium text-slate-200 transition hover:bg-white/[0.07]">
              <Upload className="size-4" />
              Upload evidence
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                multiple
                className="hidden"
                onChange={addImages}
              />
            </label>
          </div>

          {images.length > 0 ? (
            <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {images.map((image, index) => (
                <div
                  key={`${image.name}-${index}`}
                  className="flex items-center justify-between gap-3 rounded-xl border border-white/[0.07] bg-black/20 px-3 py-2"
                >
                  <span className="min-w-0 truncate text-xs text-slate-400">
                    {image.name}
                  </span>

                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="shrink-0 rounded-lg p-1 text-slate-500 hover:text-white"
                    aria-label={`Remove ${image.name}`}
                  >
                    <X className="size-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        {error ? (
          <div className="mt-5 flex items-start gap-3 rounded-2xl border border-red-400/15 bg-red-400/[0.04] p-4">
            <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-300" />

            <p className="text-sm leading-6 text-red-200/80">
              {error}
            </p>
          </div>
        ) : null}

        <button
          type="button"
          disabled={loading}
          onClick={runAnalysis}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-blue-500 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              Reading economic evidence...
            </>
          ) : (
            "Analyse Economic Evidence"
          )}
        </button>
      </section>

      {analysis ? (
        <>
          <section className="premium-card rounded-[2rem] p-6 md:p-8">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">
                  Final Assessment
                </p>

                <h2 className="mt-2 text-2xl font-semibold text-white">
                  {analysis.event || "Economic Evidence"}
                </h2>

                <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
                  {analysis.summary}
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] px-4 py-3">
                  <p className="text-[10px] uppercase tracking-[0.16em] text-slate-500">
                    Classification
                  </p>
                  <p className="mt-1 text-lg font-semibold text-white">
                    {analysis.classification}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] px-4 py-3">
                  <p className="text-[10px] uppercase tracking-[0.16em] text-slate-500">
                    Confidence
                  </p>
                  <p className="mt-1 text-lg font-semibold text-white">
                    {Math.round(analysis.confidence)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6 grid gap-4 lg:grid-cols-2">
              <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-5">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                  USD Macro Bias
                </p>

                <p className="mt-2 text-2xl font-semibold text-white">
                  {analysis.usd_bias}
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  {biasDescription(analysis.usd_bias)}
                </p>

                <p className="mt-4 text-xs text-slate-500">
                  USD bias confidence:{" "}
                  <span className="font-semibold text-slate-300">
                    {Math.round(
                      analysis.usd_bias_confidence,
                    )}
                    %
                  </span>
                </p>
              </div>

              <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-5">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                  Evidence Quality
                </p>

                <p className="mt-2 text-lg font-semibold text-white">
                  {classificationDescription(
                    analysis.classification,
                  )}
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Currency detected:{" "}
                  <span className="text-slate-200">
                    {analysis.currency || "Not explicitly identified"}
                  </span>
                </p>
              </div>
            </div>
          </section>

          <section className="premium-card rounded-[2rem] p-6">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="size-5 text-blue-300" />

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">
                  Evidence Reader
                </p>

                <h2 className="mt-1 text-xl font-semibold text-white">
                  Extracted Economic Data
                </h2>
              </div>
            </div>

            {analysis.extracted_indicators.length > 0 ? (
              <div className="mt-5 overflow-x-auto">
                <table className="w-full min-w-[900px] text-sm">
                  <thead>
                    <tr className="text-left text-slate-500">
                      <th className="px-4 py-3">Indicator</th>
                      <th className="px-4 py-3">Actual</th>
                      <th className="px-4 py-3">Forecast</th>
                      <th className="px-4 py-3">Previous</th>
                      <th className="px-4 py-3">Relevance</th>
                      <th className="px-4 py-3">Interpretation</th>
                    </tr>
                  </thead>

                  <tbody>
                    {analysis.extracted_indicators.map(
                      (item, index) => (
                        <tr
                          key={`${item.indicator}-${index}`}
                          className="border-t border-white/[0.06]"
                        >
                          <td className="px-4 py-4 font-medium text-white">
                            {item.indicator}
                          </td>

                          <td className="px-4 py-4 text-slate-300">
                            {valueOrDash(item.actual)}
                          </td>

                          <td className="px-4 py-4 text-slate-300">
                            {valueOrDash(item.forecast)}
                          </td>

                          <td className="px-4 py-4 text-slate-300">
                            {valueOrDash(item.previous)}
                          </td>

                          <td className="px-4 py-4">
                            <span
                              className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold ${relevanceClass(
                                item.relevance,
                              )}`}
                            >
                              {item.relevance}
                            </span>
                          </td>

                          <td className="max-w-[360px] px-4 py-4 leading-6 text-slate-400">
                            {item.interpretation || "—"}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="mt-5 text-sm text-slate-500">
                No structured indicators were confidently extracted.
              </p>
            )}
          </section>

          <section className="grid gap-5 lg:grid-cols-2">
            <div className="premium-card rounded-3xl p-6">
              <div className="flex items-center gap-2">
                <TrendingUp className="size-5 text-emerald-300" />

                <h3 className="font-semibold text-white">
                  Positive Factors
                </h3>
              </div>

              <div className="mt-4 space-y-3">
                {analysis.positive_factors.length > 0 ? (
                  analysis.positive_factors.map(
                    (factor, index) => (
                      <div
                        key={`${factor}-${index}`}
                        className="flex gap-3 text-sm leading-6 text-slate-400"
                      >
                        <CheckCircle2 className="mt-1 size-4 shrink-0 text-emerald-300" />
                        <span>{factor}</span>
                      </div>
                    ),
                  )
                ) : (
                  <p className="text-sm text-slate-500">
                    No strong positive factors were identified.
                  </p>
                )}
              </div>
            </div>

            <div className="premium-card rounded-3xl p-6">
              <div className="flex items-center gap-2">
                <TrendingDown className="size-5 text-red-300" />

                <h3 className="font-semibold text-white">
                  Negative Factors
                </h3>
              </div>

              <div className="mt-4 space-y-3">
                {analysis.negative_factors.length > 0 ? (
                  analysis.negative_factors.map(
                    (factor, index) => (
                      <div
                        key={`${factor}-${index}`}
                        className="flex gap-3 text-sm leading-6 text-slate-400"
                      >
                        <AlertTriangle className="mt-1 size-4 shrink-0 text-red-300" />
                        <span>{factor}</span>
                      </div>
                    ),
                  )
                ) : (
                  <p className="text-sm text-slate-500">
                    No strong negative factors were identified.
                  </p>
                )}
              </div>
            </div>
          </section>

          {analysis.contradictions.length > 0 ? (
            <section className="premium-card rounded-3xl p-6">
              <div className="flex items-center gap-2">
                <AlertTriangle className="size-5 text-amber-300" />

                <h3 className="font-semibold text-white">
                  Contradictions
                </h3>
              </div>

              <div className="mt-4 space-y-3">
                {analysis.contradictions.map(
                  (item, index) => (
                    <div
                      key={`${item}-${index}`}
                      className="rounded-2xl border border-amber-400/10 bg-amber-400/[0.03] p-4 text-sm leading-6 text-slate-400"
                    >
                      {item}
                    </div>
                  ),
                )}
              </div>
            </section>
          ) : null}

          {analysis.missing_information.length > 0 ? (
            <section className="premium-card rounded-3xl p-6">
              <h3 className="font-semibold text-white">
                Missing Information
              </h3>

              <div className="mt-4 space-y-2 text-sm leading-6 text-slate-400">
                {analysis.missing_information.map(
                  (item, index) => (
                    <p key={`${item}-${index}`}>
                      • {item}
                    </p>
                  ),
                )}
              </div>
            </section>
          ) : null}

          {analysis.warnings.length > 0 ? (
            <section className="premium-card rounded-3xl p-6">
              <div className="flex items-center gap-2">
                <AlertTriangle className="size-5 text-amber-300" />

                <h3 className="font-semibold text-white">
                  Warnings
                </h3>
              </div>

              <div className="mt-4 space-y-3">
                {analysis.warnings.map(
                  (item, index) => (
                    <div
                      key={`${item}-${index}`}
                      className="rounded-2xl border border-amber-400/10 bg-amber-400/[0.03] p-4 text-sm leading-6 text-slate-400"
                    >
                      {item}
                    </div>
                  ),
                )}
              </div>
            </section>
          ) : null}

          <section className="rounded-3xl border border-blue-400/15 bg-blue-400/[0.04] p-5">
            <div className="flex gap-3">
              <ShieldCheck className="mt-0.5 size-5 shrink-0 text-blue-300" />

              <div>
                <p className="text-sm font-medium text-slate-300">
                  Economic interpretation only
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  {analysis.disclaimer}
                </p>
              </div>
            </div>
          </section>
        </>
      ) : null}

      <section>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-white">
            More Macro Engines
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Event-specific engines can be expanded without changing the
            general evidence reader.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {["CPI", "PPI", "FOMC"].map((event) => (
            <div
              key={event}
              className="premium-card rounded-3xl p-5 opacity-70"
            >
              <Clock3 className="size-5 text-slate-500" />

              <h3 className="mt-4 font-semibold text-white">
                {event} Analyzer
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Event-specific intelligence is coming soon.
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
