import {
  useMemo,
  useState,
  type FormEvent,
} from "react"

import {
  BrainCircuit,
  CalendarRange,
  Filter,
  Gauge,
  Pencil,
  Paperclip,
  Plus,
  Search,
  Trash2,
  X,
} from "lucide-react"

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  createTrade,
  deleteTrade,
  fetchTradeReview,
  fetchTrades,
  updateTrade,
} from "@/api/trades"

import type {
  Trade,
  TradePayload,
  TradeReview,
} from "@/types/trade"

import TradeMediaPanel from "@/components/trades/TradeMediaPanel"


type ResultFilter =
  | "ALL"
  | "WIN"
  | "LOSS"
  | "BREAKEVEN"

type DirectionFilter =
  | "ALL"
  | "BUY"
  | "SELL"

type SourceFilter =
  | "ALL"
  | "MANUAL"
  | "IMPORTED"


const emptyForm = {
  broker: "Manual",
  ticket: "",
  pair: "XAUUSD",
  direction:
    "BUY" as
      | "BUY"
      | "SELL",
  entry: "",
  exit_price: "",
  stop_loss: "",
  take_profit: "",
  lot_size: "",
  profit: "",
  strategy: "",
  emotion: "",
  notes: "",
}


function money(
  value?: number | null,
) {
  return new Intl.NumberFormat(
    "en-US",
    {
      style: "currency",
      currency: "USD",
    },
  ).format(
    Number(value || 0),
  )
}


function tradeTimestamp(
  trade: Trade,
) {
  return (
    trade.closed_at ||
    trade.opened_at ||
    trade.created_at
  )
}


function tradeDate(
  trade: Trade,
) {
  const source =
    tradeTimestamp(
      trade,
    )

  if (!source) {
    return ""
  }

  return new Date(
    source,
  )
    .toISOString()
    .slice(
      0,
      10,
    )
}


function tradeSession(
  trade: Trade,
) {
  const source =
    trade.opened_at ||
    trade.created_at

  if (!source) {
    return "Unknown"
  }

  const hour =
    new Date(
      source,
    ).getUTCHours()

  if (
    hour >= 0 &&
    hour < 7
  ) {
    return "Asia"
  }

  if (
    hour >= 7 &&
    hour < 12
  ) {
    return "London"
  }

  if (
    hour >= 12 &&
    hour < 16
  ) {
    return "London / New York"
  }

  if (
    hour >= 16 &&
    hour < 21
  ) {
    return "New York"
  }

  return "After Hours"
}


function calculateR(
  trade: Trade,
) {
  if (
    trade.exit_price == null
  ) {
    return null
  }

  const risk =
    Math.abs(
      Number(
        trade.entry,
      ) -
      Number(
        trade.stop_loss,
      ),
    )

  if (
    risk <= 0
  ) {
    return null
  }

  const reward =
    trade.direction ===
    "BUY"
      ? Number(
          trade.exit_price,
        ) -
        Number(
          trade.entry,
        )
      : Number(
          trade.entry,
        ) -
        Number(
          trade.exit_price,
        )

  return (
    reward /
    risk
  )
}


function resultOf(
  trade: Trade,
): ResultFilter {
  const profit =
    Number(
      trade.profit ||
      0,
    )

  if (
    profit > 0
  ) {
    return "WIN"
  }

  if (
    profit < 0
  ) {
    return "LOSS"
  }

  return "BREAKEVEN"
}


export default function TradesPage() {
  const queryClient =
    useQueryClient()

  const [
    search,
    setSearch,
  ] = useState("")

  const [
    symbolFilter,
    setSymbolFilter,
  ] = useState("ALL")

  const [
    brokerFilter,
    setBrokerFilter,
  ] = useState("ALL")

  const [
    strategyFilter,
    setStrategyFilter,
  ] = useState("ALL")

  const [
    emotionFilter,
    setEmotionFilter,
  ] = useState("ALL")

  const [
    sessionFilter,
    setSessionFilter,
  ] = useState("ALL")

  const [
    directionFilter,
    setDirectionFilter,
  ] = useState<DirectionFilter>(
    "ALL",
  )

  const [
    resultFilter,
    setResultFilter,
  ] = useState<ResultFilter>(
    "ALL",
  )

  const [
    sourceFilter,
    setSourceFilter,
  ] = useState<SourceFilter>(
    "ALL",
  )

  const [
    dateFrom,
    setDateFrom,
  ] = useState("")

  const [
    dateTo,
    setDateTo,
  ] = useState("")

  const [
    filtersOpen,
    setFiltersOpen,
  ] = useState(false)

  const [
    formOpen,
    setFormOpen,
  ] = useState(false)

  const [
    editingTrade,
    setEditingTrade,
  ] = useState<Trade | null>(
    null,
  )

  const [
    form,
    setForm,
  ] = useState(
    emptyForm,
  )

  const [
    mediaTrade,
    setMediaTrade,
  ] = useState<Trade | null>(
    null,
  )


  const [
    review,
    setReview,
  ] = useState<{
    trade: Trade
    data?: TradeReview
    loading?: boolean
    error?: string
  } | null>(
    null,
  )


  const tradesQuery =
    useQuery({
      queryKey: [
        "trades",
      ],

      queryFn:
        fetchTrades,
    })


  const createMutation =
    useMutation({
      mutationFn:
        createTrade,

      onSuccess:
        async () => {
          await queryClient.invalidateQueries({
            queryKey: [
              "trades",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "dashboard",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "trading-calendar",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "advanced-analytics",
            ],
          })

          setFormOpen(
            false,
          )
        },
    })


  const updateMutation =
    useMutation({
      mutationFn:
        ({
          id,
          payload,
        }: {
          id: number
          payload:
            Partial<TradePayload>
        }) =>
          updateTrade(
            id,
            payload,
          ),

      onSuccess:
        async () => {
          await queryClient.invalidateQueries({
            queryKey: [
              "trades",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "dashboard",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "trading-calendar",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "advanced-analytics",
            ],
          })

          setFormOpen(
            false,
          )

          setEditingTrade(
            null,
          )
        },
    })


  const deleteMutation =
    useMutation({
      mutationFn:
        deleteTrade,

      onSuccess:
        async () => {
          await queryClient.invalidateQueries({
            queryKey: [
              "trades",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "dashboard",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "trading-calendar",
            ],
          })

          await queryClient.invalidateQueries({
            queryKey: [
              "advanced-analytics",
            ],
          })
        },
    })


  const trades =
    tradesQuery.data
      ?.trades ??
    []


  const symbols =
    useMemo(
      () =>
        Array.from(
          new Set(
            trades
              .map(
                (
                  trade,
                ) =>
                  trade.pair,
              )
              .filter(
                Boolean,
              ),
          ),
        ).sort(),
      [
        trades,
      ],
    )


  const brokers =
    useMemo(
      () =>
        Array.from(
          new Set(
            trades
              .map(
                (
                  trade,
                ) =>
                  trade.broker ||
                  "Manual",
              )
              .filter(
                Boolean,
              ),
          ),
        ).sort(),
      [
        trades,
      ],
    )


  const strategies =
    useMemo(
      () =>
        Array.from(
          new Set(
            trades
              .map(
                (
                  trade,
                ) =>
                  trade.strategy ||
                  "Unspecified",
              )
              .filter(
                Boolean,
              ),
          ),
        ).sort(),
      [
        trades,
      ],
    )


  const emotions =
    useMemo(
      () =>
        Array.from(
          new Set(
            trades
              .map(
                (
                  trade,
                ) =>
                  trade.emotion ||
                  "Unspecified",
              )
              .filter(
                Boolean,
              ),
          ),
        ).sort(),
      [
        trades,
      ],
    )


  const sessions =
    useMemo(
      () =>
        Array.from(
          new Set(
            trades.map(
              tradeSession,
            ),
          ),
        ).sort(),
      [
        trades,
      ],
    )


  const filteredTrades =
    useMemo(
      () => {
        const query =
          search
            .trim()
            .toLowerCase()

        return trades.filter(
          (
            trade,
          ) => {
            const matchesSearch =
              !query ||
              [
                trade.pair,
                trade.strategy,
                trade.broker,
                trade.ticket,
                trade.notes,
                trade.emotion,
              ]
                .filter(
                  Boolean,
                )
                .some(
                  (
                    value,
                  ) =>
                    String(
                      value,
                    )
                      .toLowerCase()
                      .includes(
                        query,
                      ),
                )

            const matchesSymbol =
              symbolFilter ===
                "ALL" ||
              trade.pair ===
                symbolFilter

            const matchesBroker =
              brokerFilter ===
                "ALL" ||
              (
                trade.broker ||
                "Manual"
              ) ===
                brokerFilter

            const matchesStrategy =
              strategyFilter ===
                "ALL" ||
              (
                trade.strategy ||
                "Unspecified"
              ) ===
                strategyFilter

            const matchesEmotion =
              emotionFilter ===
                "ALL" ||
              (
                trade.emotion ||
                "Unspecified"
              ) ===
                emotionFilter

            const session =
              tradeSession(
                trade,
              )

            const matchesSession =
              sessionFilter ===
                "ALL" ||
              session ===
                sessionFilter

            const matchesDirection =
              directionFilter ===
                "ALL" ||
              trade.direction ===
                directionFilter

            const matchesResult =
              resultFilter ===
                "ALL" ||
              resultOf(
                trade,
              ) ===
                resultFilter

            const isImported =
              Boolean(
                (
                  trade as Trade & {
                    imported?: boolean
                  }
                ).imported,
              )

            const matchesSource =
              sourceFilter ===
                "ALL" ||
              (
                sourceFilter ===
                  "IMPORTED" &&
                isImported
              ) ||
              (
                sourceFilter ===
                  "MANUAL" &&
                !isImported
              )

            const date =
              tradeDate(
                trade,
              )

            const matchesFrom =
              !dateFrom ||
              (
                date &&
                date >=
                  dateFrom
              )

            const matchesTo =
              !dateTo ||
              (
                date &&
                date <=
                  dateTo
              )

            return (
              matchesSearch &&
              matchesSymbol &&
              matchesBroker &&
              matchesStrategy &&
              matchesEmotion &&
              matchesSession &&
              matchesDirection &&
              matchesResult &&
              matchesSource &&
              matchesFrom &&
              matchesTo
            )
          },
        )
      },
      [
        trades,
        search,
        symbolFilter,
        brokerFilter,
        strategyFilter,
        emotionFilter,
        sessionFilter,
        directionFilter,
        resultFilter,
        sourceFilter,
        dateFrom,
        dateTo,
      ],
    )


  const filteredProfit =
    filteredTrades.reduce(
      (
        total,
        trade,
      ) =>
        total +
        Number(
          trade.profit ||
          0,
        ),
      0,
    )


  const filteredWins =
    filteredTrades.filter(
      (
        trade,
      ) =>
        Number(
          trade.profit ||
          0,
        ) > 0,
    ).length


  const filteredLosses =
    filteredTrades.filter(
      (
        trade,
      ) =>
        Number(
          trade.profit ||
          0,
        ) < 0,
    ).length


  const filteredWinRate =
    filteredTrades.length
      ? (
          filteredWins /
          filteredTrades.length
        ) *
        100
      : 0


  const averageRValues =
    filteredTrades
      .map(
        calculateR,
      )
      .filter(
        (
          value,
        ): value is number =>
          value !== null,
      )


  const averageR =
    averageRValues.length
      ? averageRValues.reduce(
          (
            total,
            value,
          ) =>
            total +
            value,
          0,
        ) /
        averageRValues.length
      : 0


  function clearFilters() {
    setSearch("")
    setSymbolFilter(
      "ALL",
    )
    setBrokerFilter(
      "ALL",
    )
    setStrategyFilter(
      "ALL",
    )
    setEmotionFilter(
      "ALL",
    )
    setSessionFilter(
      "ALL",
    )
    setDirectionFilter(
      "ALL",
    )
    setResultFilter(
      "ALL",
    )
    setSourceFilter(
      "ALL",
    )
    setDateFrom("")
    setDateTo("")
  }


  function openNewTrade() {
    setEditingTrade(
      null,
    )

    setForm(
      emptyForm,
    )

    setFormOpen(
      true,
    )
  }


  function openEditTrade(
    trade: Trade,
  ) {
    setEditingTrade(
      trade,
    )

    setForm({
      broker:
        trade.broker ??
        "",

      ticket:
        trade.ticket ??
        "",

      pair:
        trade.pair,

      direction:
        trade.direction,

      entry:
        String(
          trade.entry,
        ),

      exit_price:
        String(
          trade.exit_price ??
          "",
        ),

      stop_loss:
        String(
          trade.stop_loss,
        ),

      take_profit:
        String(
          trade.take_profit,
        ),

      lot_size:
        String(
          trade.lot_size ??
          "",
        ),

      profit:
        String(
          trade.profit ??
          "",
        ),

      strategy:
        trade.strategy ??
        "",

      emotion:
        trade.emotion ??
        "",

      notes:
        trade.notes ??
        "",
    })

    setFormOpen(
      true,
    )
  }


  async function submitTrade(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const payload:
      TradePayload = {
      broker:
        form.broker.trim() ||
        null,

      ticket:
        form.ticket.trim() ||
        null,

      pair:
        form.pair
          .trim()
          .toUpperCase(),

      direction:
        form.direction,

      entry:
        Number(
          form.entry,
        ),

      exit_price:
        form.exit_price.trim() ===
        ""
          ? null
          : Number(
              form.exit_price,
            ),

      stop_loss:
        Number(
          form.stop_loss,
        ),

      take_profit:
        Number(
          form.take_profit,
        ),

      lot_size:
        form.lot_size.trim() ===
        ""
          ? null
          : Number(
              form.lot_size,
            ),

      profit:
        form.profit.trim() ===
        ""
          ? null
          : Number(
              form.profit,
            ),

      commission:
        0,

      swap:
        0,

      strategy:
        form.strategy.trim() ||
        null,

      emotion:
        form.emotion.trim() ||
        null,

      notes:
        form.notes.trim() ||
        null,

      imported:
        false,
    }

    if (
      editingTrade
    ) {
      await updateMutation.mutateAsync({
        id:
          editingTrade.id,

        payload,
      })
    }
    else {
      await createMutation.mutateAsync(
        payload,
      )
    }
  }


  async function openTradeReview(
    trade: Trade,
  ) {
    setReview({
      trade,
      loading:
        true,
    })

    try {
      const data =
        await fetchTradeReview(
          trade.id,
        )

      setReview({
        trade,
        data,
      })
    }
    catch {
      setReview({
        trade,
        error:
          "Unable to generate this trade review.",
      })
    }
  }


  return (
    <div className="space-y-6">

      <section className="premium-card grid-surface rounded-[2rem] p-6 sm:p-8">

        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">

          <div>

            <p className="text-xs uppercase tracking-[0.25em] text-blue-300">
              Advanced Trade Journal
            </p>

            <h2 className="mt-4 text-3xl font-semibold sm:text-4xl">
              Every trade becomes intelligence.
            </h2>

            <p className="mt-3 max-w-2xl text-slate-400">
              Filter your trading history,
              compare sessions and strategies,
              inspect psychology and measure
              R-multiple performance.
            </p>

          </div>


          <button
            type="button"
            onClick={
              openNewTrade
            }
            className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-3 font-semibold text-white"
          >
            <Plus className="size-4" />
            Add trade
          </button>

        </div>

      </section>


      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Filtered P&L
          </p>

          <p
            className={[
              "mt-2 text-3xl font-semibold",

              filteredProfit >= 0
                ? "text-emerald-300"
                : "text-red-300",

            ].join(" ")}
          >
            {money(
              filteredProfit,
            )}
          </p>

          <p className="mt-2 text-xs text-slate-500">
            {filteredTrades.length} matching trades
          </p>

        </div>


        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Win Rate
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {filteredWinRate.toFixed(
              1,
            )}
            %
          </p>

          <p className="mt-2 text-xs text-slate-500">
            {filteredWins} wins ·{" "}
            {filteredLosses} losses
          </p>

        </div>


        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Average R
          </p>

          <p
            className={[
              "mt-2 text-3xl font-semibold",

              averageR >= 0
                ? "text-emerald-300"
                : "text-red-300",

            ].join(" ")}
          >
            {averageR.toFixed(
              2,
            )}
            R
          </p>

          <p className="mt-2 text-xs text-slate-500">
            {averageRValues.length} trades with R data
          </p>

        </div>


        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Total Trades
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {trades.length}
          </p>

          <p className="mt-2 text-xs text-slate-500">
            {filteredTrades.length} currently visible
          </p>

        </div>

      </section>


      <section className="premium-card rounded-[2rem] p-4 sm:p-5">

        <div className="flex flex-col gap-3 lg:flex-row">

          <div className="flex flex-1 items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.03] px-4">

            <Search className="size-4 shrink-0 text-slate-500" />

            <input
              value={
                search
              }
              onChange={(
                event,
              ) =>
                setSearch(
                  event.target.value,
                )
              }
              placeholder="Search pair, strategy, broker, emotion, ticket or notes..."
              className="w-full bg-transparent py-3 outline-none"
            />

          </div>


          <button
            type="button"
            onClick={() =>
              setFiltersOpen(
                (
                  value,
                ) =>
                  !value,
              )
            }
            className="flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/[0.03] px-5 py-3"
          >
            <Filter className="size-4" />
            Filters
          </button>


          <button
            type="button"
            onClick={
              clearFilters
            }
            className="rounded-2xl border border-white/10 px-5 py-3 text-sm text-slate-400"
          >
            Clear
          </button>

        </div>


        {filtersOpen && (
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">

            <select
              value={
                symbolFilter
              }
              onChange={(
                event,
              ) =>
                setSymbolFilter(
                  event.target.value,
                )
              }
              className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="ALL">
                All symbols
              </option>

              {symbols.map(
                (
                  value,
                ) => (
                  <option
                    key={
                      value
                    }
                    value={
                      value
                    }
                  >
                    {value}
                  </option>
                ),
              )}
            </select>


            <select
              value={
                brokerFilter
              }
              onChange={(
                event,
              ) =>
                setBrokerFilter(
                  event.target.value,
                )
              }
              className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="ALL">
                All brokers
              </option>

              {brokers.map(
                (
                  value,
                ) => (
                  <option
                    key={
                      value
                    }
                    value={
                      value
                    }
                  >
                    {value}
                  </option>
                ),
              )}
            </select>


            <select
              value={
                strategyFilter
              }
              onChange={(
                event,
              ) =>
                setStrategyFilter(
                  event.target.value,
                )
              }
              className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="ALL">
                All strategies
              </option>

              {strategies.map(
                (
                  value,
                ) => (
                  <option
                    key={
                      value
                    }
                    value={
                      value
                    }
                  >
                    {value}
                  </option>
                ),
              )}
            </select>


            <select
              value={
                emotionFilter
              }
              onChange={(
                event,
              ) =>
                setEmotionFilter(
                  event.target.value,
                )
              }
              className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="ALL">
                All emotions
              </option>

              {emotions.map(
                (
                  value,
                ) => (
                  <option
                    key={
                      value
                    }
                    value={
                      value
                    }
                  >
                    {value}
                  </option>
                ),
              )}
            </select>


            <select
              value={
                sessionFilter
              }
              onChange={(
                event,
              ) =>
                setSessionFilter(
                  event.target.value,
                )
              }
              className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="ALL">
                All sessions
              </option>

              {sessions.map(
                (
                  value,
                ) => (
                  <option
                    key={
                      value
                    }
                    value={
                      value
                    }
                  >
                    {value}
                  </option>
                ),
              )}
            </select>


            <select
              value={
                directionFilter
              }
              onChange={(
                event,
              ) =>
                setDirectionFilter(
                  event.target.value as DirectionFilter,
                )
              }
              className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="ALL">
                Buy & Sell
              </option>
              <option value="BUY">
                BUY
              </option>
              <option value="SELL">
                SELL
              </option>
            </select>


            <select
              value={
                resultFilter
              }
              onChange={(
                event,
              ) =>
                setResultFilter(
                  event.target.value as ResultFilter,
                )
              }
              className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="ALL">
                All results
              </option>
              <option value="WIN">
                Wins
              </option>
              <option value="LOSS">
                Losses
              </option>
              <option value="BREAKEVEN">
                Breakeven
              </option>
            </select>


            <select
              value={
                sourceFilter
              }
              onChange={(
                event,
              ) =>
                setSourceFilter(
                  event.target.value as SourceFilter,
                )
              }
              className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
            >
              <option value="ALL">
                All sources
              </option>
              <option value="MANUAL">
                Manual
              </option>
              <option value="IMPORTED">
                Imported
              </option>
            </select>


            <label className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">

              <span className="flex items-center gap-2 text-xs text-slate-500">
                <CalendarRange className="size-4" />
                From
              </span>

              <input
                type="date"
                value={
                  dateFrom
                }
                onChange={(
                  event,
                ) =>
                  setDateFrom(
                    event.target.value,
                  )
                }
                className="mt-2 w-full bg-transparent outline-none"
              />

            </label>


            <label className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">

              <span className="flex items-center gap-2 text-xs text-slate-500">
                <CalendarRange className="size-4" />
                To
              </span>

              <input
                type="date"
                value={
                  dateTo
                }
                onChange={(
                  event,
                ) =>
                  setDateTo(
                    event.target.value,
                  )
                }
                className="mt-2 w-full bg-transparent outline-none"
              />

            </label>

          </div>
        )}

      </section>


      {tradesQuery.isLoading ? (
        <div className="grid min-h-[320px] place-items-center">

          <div className="size-10 animate-spin rounded-full border-2 border-blue-400/20 border-t-blue-400" />

        </div>
      ) : tradesQuery.isError ? (
        <div className="premium-card rounded-[2rem] p-8 text-red-300">
          Unable to load trades.
        </div>
      ) : (
        <div className="premium-card overflow-x-auto rounded-[2rem]">

          <table className="w-full min-w-[1250px] text-left">

            <thead className="border-b border-white/10 text-xs uppercase tracking-[0.15em] text-slate-500">

              <tr>
                <th className="px-5 py-4">
                  Market
                </th>
                <th className="px-5 py-4">
                  Direction
                </th>
                <th className="px-5 py-4">
                  Session
                </th>
                <th className="px-5 py-4">
                  Entry
                </th>
                <th className="px-5 py-4">
                  Exit
                </th>
                <th className="px-5 py-4">
                  R
                </th>
                <th className="px-5 py-4">
                  Profit
                </th>
                <th className="px-5 py-4">
                  Strategy
                </th>
                <th className="px-5 py-4">
                  Psychology
                </th>
                <th className="px-5 py-4">
                  Date
                </th>
                <th className="px-5 py-4">
                  Actions
                </th>
              </tr>

            </thead>


            <tbody className="divide-y divide-white/[0.06]">

              {filteredTrades.map(
                (
                  trade,
                ) => {
                  const r =
                    calculateR(
                      trade,
                    )

                  const profit =
                    Number(
                      trade.profit ||
                      0,
                    )

                  return (
                    <tr
                      key={
                        trade.id
                      }
                      className="transition hover:bg-white/[0.02]"
                    >

                      <td className="px-5 py-4">

                        <p className="font-semibold">
                          {trade.pair}
                        </p>

                        <p className="text-xs text-slate-500">
                          {trade.broker ||
                            "Manual"}{" "}
                          ·{" "}
                          {trade.ticket ||
                            `#${trade.id}`}
                        </p>

                      </td>


                      <td
                        className={[
                          "px-5 py-4 font-semibold",

                          trade.direction ===
                          "BUY"
                            ? "text-emerald-300"
                            : "text-red-300",

                        ].join(" ")}
                      >
                        {trade.direction}
                      </td>


                      <td className="px-5 py-4">
                        {tradeSession(
                          trade,
                        )}
                      </td>


                      <td className="px-5 py-4">
                        {trade.entry}
                      </td>


                      <td className="px-5 py-4">
                        {trade.exit_price ??
                          "—"}
                      </td>


                      <td className="px-5 py-4">

                        <span
                          className={[
                            "inline-flex items-center gap-1 rounded-xl px-2.5 py-1 text-xs font-semibold",

                            r == null
                              ? "bg-white/[0.04] text-slate-500"

                              : r >=
                                0
                              ? "bg-emerald-400/[0.08] text-emerald-300"

                              : "bg-red-400/[0.08] text-red-300",

                          ].join(" ")}
                        >

                          <Gauge className="size-3.5" />

                          {r == null
                            ? "—"
                            : `${r.toFixed(
                                2,
                              )}R`}

                        </span>

                      </td>


                      <td
                        className={[
                          "px-5 py-4 font-semibold",

                          profit >= 0
                            ? "text-emerald-300"
                            : "text-red-300",

                        ].join(" ")}
                      >
                        {money(
                          profit,
                        )}
                      </td>


                      <td className="px-5 py-4">
                        {trade.strategy ||
                          "Unspecified"}
                      </td>


                      <td className="px-5 py-4">
                        {trade.emotion ||
                          "Unspecified"}
                      </td>


                      <td className="px-5 py-4 text-sm text-slate-400">
                        {tradeDate(
                          trade,
                        ) ||
                          "—"}
                      </td>


                      <td className="px-5 py-4">

                        <div className="flex gap-2">

                          <button
                            type="button"
                            onClick={() =>
                              setMediaTrade(
                                trade,
                              )
                            }
                            className="grid size-9 place-items-center rounded-xl bg-indigo-400/10 text-indigo-300"
                            title="Trade media"
                          >
                            <Paperclip className="size-4" />
                          </button>


                          <button
                            type="button"
                            onClick={() =>
                              openTradeReview(
                                trade,
                              )
                            }
                            className="grid size-9 place-items-center rounded-xl bg-blue-400/10 text-blue-300"
                            title="AI review"
                          >
                            <BrainCircuit className="size-4" />
                          </button>


                          <button
                            type="button"
                            onClick={() =>
                              openEditTrade(
                                trade,
                              )
                            }
                            className="grid size-9 place-items-center rounded-xl bg-white/[0.04]"
                            title="Edit"
                          >
                            <Pencil className="size-4" />
                          </button>


                          <button
                            type="button"
                            onClick={() => {
                              if (
                                window.confirm(
                                  "Delete this trade?",
                                )
                              ) {
                                deleteMutation.mutate(
                                  trade.id,
                                )
                              }
                            }}
                            className="grid size-9 place-items-center rounded-xl bg-red-400/10 text-red-300"
                            title="Delete"
                          >
                            <Trash2 className="size-4" />
                          </button>

                        </div>

                      </td>

                    </tr>
                  )
                },
              )}

            </tbody>

          </table>


          {!filteredTrades.length && (
            <div className="p-10 text-center text-slate-500">
              No trades match the selected filters.
            </div>
          )}

        </div>
      )}


      {formOpen && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur-sm">

          <div className="premium-card max-h-[92vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] p-7">

            <div className="flex items-start justify-between">

              <div>

                <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
                  {editingTrade
                    ? "Edit trade"
                    : "New trade"}
                </p>

                <h3 className="mt-2 text-2xl font-semibold">
                  {editingTrade
                    ? editingTrade.pair
                    : "Add journal entry"}
                </h3>

              </div>


              <button
                type="button"
                onClick={() =>
                  setFormOpen(
                    false,
                  )
                }
              >
                <X />
              </button>

            </div>


            <form
              onSubmit={
                submitTrade
              }
              className="mt-6 space-y-4"
            >

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

                <input
                  placeholder="Pair"
                  required
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={
                    form.pair
                  }
                  onChange={(
                    event,
                  ) =>
                    setForm({
                      ...form,
                      pair:
                        event.target.value,
                    })
                  }
                />


                <select
                  className="rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
                  value={
                    form.direction
                  }
                  onChange={(
                    event,
                  ) =>
                    setForm({
                      ...form,
                      direction:
                        event.target.value as
                          | "BUY"
                          | "SELL",
                    })
                  }
                >
                  <option value="BUY">
                    BUY
                  </option>
                  <option value="SELL">
                    SELL
                  </option>
                </select>


                <input
                  placeholder="Broker"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={
                    form.broker
                  }
                  onChange={(
                    event,
                  ) =>
                    setForm({
                      ...form,
                      broker:
                        event.target.value,
                    })
                  }
                />


                <input
                  placeholder="Ticket"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={
                    form.ticket
                  }
                  onChange={(
                    event,
                  ) =>
                    setForm({
                      ...form,
                      ticket:
                        event.target.value,
                    })
                  }
                />

              </div>


              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">

                {[
                  [
                    "entry",
                    "Entry",
                  ],
                  [
                    "exit_price",
                    "Exit",
                  ],
                  [
                    "stop_loss",
                    "Stop loss",
                  ],
                  [
                    "take_profit",
                    "Take profit",
                  ],
                  [
                    "lot_size",
                    "Lot size",
                  ],
                ].map(
                  (
                    [
                      key,
                      label,
                    ],
                  ) => (
                    <input
                      key={
                        key
                      }
                      type="number"
                      step="any"
                      required={
                        key ===
                          "entry" ||
                        key ===
                          "stop_loss" ||
                        key ===
                          "take_profit"
                      }
                      placeholder={
                        label
                      }
                      className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                      value={
                        form[
                          key as keyof typeof form
                        ]
                      }
                      onChange={(
                        event,
                      ) =>
                        setForm({
                          ...form,
                          [key]:
                            event.target.value,
                        })
                      }
                    />
                  ),
                )}

              </div>


              <div className="grid gap-4 md:grid-cols-3">

                <input
                  type="number"
                  step="any"
                  placeholder="Profit"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={
                    form.profit
                  }
                  onChange={(
                    event,
                  ) =>
                    setForm({
                      ...form,
                      profit:
                        event.target.value,
                    })
                  }
                />


                <input
                  placeholder="Strategy"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={
                    form.strategy
                  }
                  onChange={(
                    event,
                  ) =>
                    setForm({
                      ...form,
                      strategy:
                        event.target.value,
                    })
                  }
                />


                <input
                  placeholder="Emotion"
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                  value={
                    form.emotion
                  }
                  onChange={(
                    event,
                  ) =>
                    setForm({
                      ...form,
                      emotion:
                        event.target.value,
                    })
                  }
                />

              </div>


              <textarea
                rows={4}
                placeholder="Journal notes"
                className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3"
                value={
                  form.notes
                }
                onChange={(
                  event,
                ) =>
                  setForm({
                    ...form,
                    notes:
                      event.target.value,
                  })
                }
              />


              <div className="flex justify-end gap-3">

                <button
                  type="button"
                  onClick={() =>
                    setFormOpen(
                      false,
                    )
                  }
                  className="rounded-2xl border border-white/10 px-5 py-3"
                >
                  Cancel
                </button>


                <button
                  disabled={
                    createMutation.isPending ||
                    updateMutation.isPending
                  }
                  className="rounded-2xl bg-blue-500 px-5 py-3 font-semibold"
                >
                  {createMutation.isPending ||
                  updateMutation.isPending
                    ? "Saving..."
                    : "Save trade"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}


      {mediaTrade && (
        <TradeMediaPanel
          trade={
            mediaTrade
          }
          onClose={() =>
            setMediaTrade(
              null,
            )
          }
        />
      )}


      {review && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60">

          <aside className="h-full w-full max-w-xl overflow-y-auto border-l border-white/10 bg-[#090f1c] p-8">

            <div className="flex items-start justify-between">

              <h3 className="text-2xl font-semibold">
                AI review ·{" "}
                {review.trade.pair}
              </h3>


              <button
                type="button"
                onClick={() =>
                  setReview(
                    null,
                  )
                }
              >
                <X />
              </button>

            </div>


            {review.loading ? (
              <p className="mt-10 text-slate-400">
                Reviewing trade...
              </p>
            ) : review.error ? (
              <p className="mt-10 text-red-300">
                {review.error}
              </p>
            ) : review.data ? (
              <div className="mt-8 space-y-5">

                <div className="premium-card rounded-3xl p-5">

                  <p className="text-4xl font-semibold text-blue-300">
                    {review.data.trade_score}
                  </p>

                  <p className="mt-2">
                    {review.data.summary}
                  </p>

                </div>


                <div>

                  <h4 className="font-semibold text-emerald-300">
                    Strengths
                  </h4>

                  {review.data.strengths.map(
                    (
                      item,
                    ) => (
                      <p
                        key={
                          item
                        }
                        className="mt-2 rounded-2xl bg-emerald-400/[0.05] p-3"
                      >
                        {item}
                      </p>
                    ),
                  )}

                </div>


                <div>

                  <h4 className="font-semibold text-red-300">
                    Mistakes
                  </h4>

                  {review.data.mistakes.map(
                    (
                      item,
                    ) => (
                      <p
                        key={
                          item
                        }
                        className="mt-2 rounded-2xl bg-red-400/[0.05] p-3"
                      >
                        {item}
                      </p>
                    ),
                  )}

                </div>


                <div className="premium-card rounded-3xl p-5">

                  <strong>
                    Lesson
                  </strong>

                  <p className="mt-2 text-slate-300">
                    {review.data.lesson}
                  </p>

                </div>


                <div className="rounded-3xl bg-blue-400/[0.06] p-5">

                  <strong>
                    Next mission
                  </strong>

                  <p className="mt-2">
                    {review.data.next_mission}
                  </p>

                </div>

              </div>
            ) : null}

          </aside>

        </div>
      )}

    </div>
  )
}
