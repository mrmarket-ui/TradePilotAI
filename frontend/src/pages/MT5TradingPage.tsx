import {
  Bot,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  Link2,
  Loader2,
  RefreshCw,
  Server,
  ShieldCheck,
  Trash2,
  Unplug,
  WalletCards,
} from "lucide-react"

import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  approveMT5Proposal,
  connectMT5Account,
  disableMT5AutoTrader,
  enableMT5AutoTrader,
  getMT5Accounts,
  getMT5Proposals,
  linkMT5Strategy,
  rejectMT5Proposal,
  removeMT5Account,
  syncMT5Trades,
  unlinkMT5Strategy,
  type ConnectMT5Payload,
  type MT5BrokerAccount,
} from "@/api/mt5"

import {
  fetchStrategies,
} from "@/api/strategy"

import type {
  StrategyProfile,
} from "@/types/strategy"


function apiErrorMessage(
  error: unknown,
  fallback: string,
) {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error
  ) {
    const response =
      (
        error as {
          response?: {
            data?: {
              detail?: string
            }
          }
        }
      ).response

    if (
      typeof response?.data?.detail ===
      "string"
    ) {
      return response.data.detail
    }
  }

  if (
    error instanceof Error &&
    error.message
  ) {
    return error.message
  }

  return fallback
}


function formatLastSync(
  value: string | null,
) {
  if (!value) {
    return "Not synced yet"
  }

  const date =
    new Date(value)

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value
  }

  return date.toLocaleString()
}


function InfoChip({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <span
      className="
        rounded-full
        border border-white/10
        bg-white/[0.04]
        px-3 py-1.5
        text-xs text-slate-300
      "
    >
      {children}
    </span>
  )
}


function StrategyDetails({
  strategy,
}: {
  strategy: StrategyProfile
}) {
  return (
    <div className="mt-5 space-y-4">
      <div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
          Linked Strategy
        </p>

        <h3 className="mt-1 text-lg font-semibold text-white">
          {strategy.name}
        </h3>

        {strategy.description ? (
          <p className="mt-2 text-sm leading-6 text-slate-400">
            {strategy.description}
          </p>
        ) : null}
      </div>

      <div className="flex flex-wrap gap-2">
        {(strategy.markets || [])
          .slice(0, 5)
          .map((market) => (
            <InfoChip key={market}>
              {market}
            </InfoChip>
          ))}

        {(strategy.timeframes || [])
          .slice(0, 5)
          .map((timeframe) => (
            <InfoChip
              key={timeframe}
            >
              {timeframe}
            </InfoChip>
          ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
          <p className="text-xs text-slate-500">
            Max Risk
          </p>

          <p className="mt-1 font-semibold text-white">
            {strategy.max_risk_percent}%
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
          <p className="text-xs text-slate-500">
            Max Trades / Day
          </p>

          <p className="mt-1 font-semibold text-white">
            {strategy.max_trades_per_day}
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
          <p className="text-xs text-slate-500">
            Daily Loss Limit
          </p>

          <p className="mt-1 font-semibold text-white">
            {strategy.max_daily_loss_percent}%
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
          <p className="text-xs text-slate-500">
            Trade Approval
          </p>

          <p className="mt-1 font-semibold text-white">
            {strategy.requires_user_approval
              ? "Required"
              : "Configured off"}
          </p>
        </div>
      </div>
    </div>
  )
}



function formatProposalPrice(
  value: number,
) {
  if (!Number.isFinite(value)) {
    return String(value)
  }

  return value.toFixed(5)
}


function proposalTimeRemaining(
  expiresAt: string,
  nowMs: number,
) {
  const normalizedExpiresAt =
    /(?:Z|[+-]\d{2}:\d{2})$/i.test(
      expiresAt,
    )
      ? expiresAt
      : `${expiresAt}Z`

  const expires =
    new Date(
      normalizedExpiresAt,
    ).getTime()

  if (
    Number.isNaN(expires)
  ) {
    return "Unknown"
  }

  const remaining =
    expires - nowMs

  if (remaining <= 0) {
    return "Expired"
  }

  const totalSeconds =
    Math.floor(
      remaining / 1000,
    )

  const minutes =
    Math.floor(
      totalSeconds / 60,
    )

  const seconds =
    totalSeconds % 60

  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
}


function proposalRuleLabel(
  rule: unknown,
) {
  if (
    typeof rule === "string"
  ) {
    return rule
  }

  try {
    return JSON.stringify(rule)
  } catch {
    return String(rule)
  }
}


export default function MT5TradingPage() {
  const qc =
    useQueryClient()

  const [
    broker,
    setBroker,
  ] = useState("")

  const [
    server,
    setServer,
  ] = useState("")

  const [
    accountNumber,
    setAccountNumber,
  ] = useState("")

  const [
    password,
    setPassword,
  ] = useState("")

  const [
    selectedStrategies,
    setSelectedStrategies,
  ] = useState<
    Record<number, string>
  >({})

  const [
    autoTraderHoldMinutes,
    setAutoTraderHoldMinutes,
  ] = useState<
    Record<number, 30 | 60>
  >({})


  const [
    message,
    setMessage,
  ] = useState("")

  const [
    error,
    setError,
  ] = useState("")


  const [
    nowMs,
    setNowMs,
  ] = useState(
    Date.now(),
  )


  useEffect(() => {
    const timer =
      window.setInterval(
        () => {
          setNowMs(
            Date.now(),
          )
        },
        1000,
      )

    return () => {
      window.clearInterval(
        timer,
      )
    }
  }, [])


  const accountsQuery =
    useQuery({
      queryKey: [
        "mt5-accounts",
      ],

      queryFn:
        getMT5Accounts,
    })


  const strategiesQuery =
    useQuery({
      queryKey: [
        "strategies",
      ],

      queryFn:
        fetchStrategies,
    })


  const pendingProposalsQuery =
    useQuery({
      queryKey: [
        "mt5-proposals",
        "pending",
      ],

      queryFn: () =>
        getMT5Proposals(
          "pending",
        ),

      refetchInterval:
        5000,
    })


  const strategies =
    useMemo(() => {
      const data =
        strategiesQuery.data

      if (!data) {
        return []
      }

      if (Array.isArray(data)) {
        return data as StrategyProfile[]
      }

      return data.strategies || []
    }, [
      strategiesQuery.data,
    ])


  const activeStrategies =
    useMemo(
      () =>
        strategies.filter(
          (strategy) =>
            strategy.is_active,
        ),
      [strategies],
    )


  const strategyById =
    useMemo(
      () =>
        new Map(
          strategies.map(
            (strategy) => [
              strategy.id,
              strategy,
            ],
          ),
        ),
      [strategies],
    )


  const resetFeedback = () => {
    setMessage("")
    setError("")
  }


  const refreshAccounts =
    async () => {
      await qc.invalidateQueries({
        queryKey: [
          "mt5-accounts",
        ],
      })
    }


  const refreshProposals =
    async () => {
      await qc.invalidateQueries({
        queryKey: [
          "mt5-proposals",
        ],
      })
    }


  const connectMutation =
    useMutation({
      mutationFn:
        (
          payload:
            ConnectMT5Payload,
        ) =>
          connectMT5Account(
            payload,
          ),

      onMutate:
        resetFeedback,

      onSuccess:
        async () => {
          setMessage(
            "MT5 account linked successfully.",
          )

          setPassword("")
          setAccountNumber("")

          await refreshAccounts()
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to connect the MT5 account.",
            ),
          )
        },
    })


  const linkMutation =
    useMutation({
      mutationFn:
        ({
          accountId,
          strategyId,
        }: {
          accountId: number
          strategyId: number
        }) =>
          linkMT5Strategy(
            accountId,
            strategyId,
          ),

      onMutate:
        resetFeedback,

      onSuccess:
        async () => {
          setMessage(
            "Strategy Brain strategy linked to MT5.",
          )

          await refreshAccounts()
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to link the strategy.",
            ),
          )
        },
    })


  const unlinkMutation =
    useMutation({
      mutationFn:
        unlinkMT5Strategy,

      onMutate:
        resetFeedback,

      onSuccess:
        async () => {
          setMessage(
            "Strategy unlinked from the MT5 account.",
          )

          await refreshAccounts()
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to unlink the strategy.",
            ),
          )
        },
    })


  const removeMutation =
    useMutation({
      mutationFn:
        removeMT5Account,

      onMutate:
        resetFeedback,

      onSuccess:
        async () => {
          setMessage(
            "MT5 account removed.",
          )

          await refreshAccounts()
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to remove the MT5 account.",
            ),
          )
        },
    })


  const enableAutoTraderMutation =
    useMutation({
      mutationFn:
        ({
          accountId,
          maxHoldMinutes,
        }: {
          accountId: number
          maxHoldMinutes: 30 | 60
        }) =>
          enableMT5AutoTrader(
            accountId,
            maxHoldMinutes,
          ),

      onMutate:
        resetFeedback,

      onSuccess:
        async (account) => {
          setMessage(
            `AutoTrader monitoring enabled for ${account.broker}. Trader approval is still required before every live order.`,
          )

          await refreshAccounts()
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to enable AutoTrader.",
            ),
          )
        },
    })


  const disableAutoTraderMutation =
    useMutation({
      mutationFn:
        disableMT5AutoTrader,

      onMutate:
        resetFeedback,

      onSuccess:
        async (account) => {
          setMessage(
            `AutoTrader monitoring disabled for ${account.broker}.`,
          )

          await refreshAccounts()
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to disable AutoTrader.",
            ),
          )
        },
    })

  const approveProposalMutation =
    useMutation({
      mutationFn:
        approveMT5Proposal,

      onMutate:
        resetFeedback,

      onSuccess:
        async (proposal) => {
          setMessage(
            `${proposal.symbol} trade approved. Approval recorded securely. No MT5 order has been sent yet.`,
          )

          await qc.invalidateQueries({
            queryKey: [
              "mt5-proposals",
            ],
          })
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to approve the trade proposal.",
            ),
          )
        },
    })


  const rejectProposalMutation =
    useMutation({
      mutationFn:
        rejectMT5Proposal,

      onMutate:
        resetFeedback,

      onSuccess:
        async (proposal) => {
          setMessage(
            `${proposal.symbol} trade proposal rejected.`,
          )

          await qc.invalidateQueries({
            queryKey: [
              "mt5-proposals",
            ],
          })
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to reject the trade proposal.",
            ),
          )
        },
    })


  const syncMutation =
    useMutation({
      mutationFn:
        syncMT5Trades,

      onMutate:
        resetFeedback,

      onSuccess:
        async (result) => {
          setMessage(
            result.status ===
              "success"
              ? `MT5 sync complete. ${result.imported} imported, ${result.skipped} skipped.`
              : `MT5 sync partially completed. ${result.imported} imported.`,
          )

          await refreshAccounts()

          await qc.invalidateQueries({
            queryKey: [
              "trades",
            ],
          })
        },

      onError:
        (err) => {
          setError(
            apiErrorMessage(
              err,
              "Unable to sync MT5 trades.",
            ),
          )
        },
    })


  const handleConnect =
    (
      event:
        React.FormEvent,
    ) => {
      event.preventDefault()

      resetFeedback()

      const parsed =
        Number(accountNumber)

      if (
        !broker.trim() ||
        !server.trim() ||
        !password ||
        !Number.isInteger(parsed) ||
        parsed <= 0
      ) {
        setError(
          "Enter the broker, MT5 server, account number and password.",
        )

        return
      }

      connectMutation.mutate({
        broker:
          broker.trim(),

        server:
          server.trim(),

        account_number:
          parsed,

        password,
      })
    }


  const accounts =
    accountsQuery.data || []


  const pendingProposals =
    (
      pendingProposalsQuery.data ||
      []
    ).filter(
      (proposal) =>
        proposal.status === "pending" &&
        proposalTimeRemaining(
          proposal.expires_at,
          nowMs,
        ) !== "Expired",
    )


  return (
    <div className="space-y-6 pb-10">
      <section className="premium-card rounded-[2rem] p-6 md:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm font-medium text-blue-300">
              <WalletCards className="h-4 w-4" />
              MT5 Trading
            </div>

            <h1 className="mt-3 text-2xl font-semibold tracking-tight text-white md:text-3xl">
              Connect MT5 to Strategy Brain
            </h1>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
              Link your MetaTrader 5 account for trade syncing,
              analysis and Strategy Brain integration. Live
              AutoTrader execution is not enabled yet.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 text-xs font-medium text-emerald-300">
            <ShieldCheck className="h-4 w-4" />
            Premium
          </div>
        </div>
      </section>


      {message ? (
        <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
          {message}
        </div>
      ) : null}


      {error ? (
        <div className="rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}


      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="premium-card rounded-[2rem] p-5 md:p-6">
          <div className="flex items-start gap-3">
            <div className="rounded-2xl border border-blue-400/20 bg-blue-400/10 p-3">
              <Server className="h-5 w-5 text-blue-300" />
            </div>

            <div>
              <h2 className="font-semibold text-white">
                Connect MT5 Account
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-400">
                Your MT5 password is sent to the backend and
                stored using the existing encrypted credential
                service. It is never returned by this page.
              </p>
            </div>
          </div>

          <form
            onSubmit={
              handleConnect
            }
            className="mt-6 space-y-4"
          >
            <label className="block">
              <span className="text-xs font-medium text-slate-400">
                Broker
              </span>

              <input
                value={broker}
                onChange={(event) =>
                  setBroker(
                    event.target.value,
                  )
                }
                placeholder="Example: HFM"
                className="mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/50"
              />
            </label>

            <label className="block">
              <span className="text-xs font-medium text-slate-400">
                MT5 Server
              </span>

              <input
                value={server}
                onChange={(event) =>
                  setServer(
                    event.target.value,
                  )
                }
                placeholder="Example: HFMarkets-Live"
                className="mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/50"
              />
            </label>

            <label className="block">
              <span className="text-xs font-medium text-slate-400">
                Account Number
              </span>

              <input
                inputMode="numeric"
                value={
                  accountNumber
                }
                onChange={(event) =>
                  setAccountNumber(
                    event.target.value,
                  )
                }
                placeholder="MT5 login number"
                className="mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/50"
              />
            </label>

            <label className="block">
              <span className="text-xs font-medium text-slate-400">
                MT5 Password
              </span>

              <input
                type="password"
                autoComplete="off"
                value={password}
                onChange={(event) =>
                  setPassword(
                    event.target.value,
                  )
                }
                placeholder="••••••••"
                className="mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/50"
              />
            </label>

            <button
              type="submit"
              disabled={
                connectMutation.isPending
              }
              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-blue-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {connectMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Link2 className="h-4 w-4" />
              )}

              {connectMutation.isPending
                ? "Connecting..."
                : "Link MT5 Account"}
            </button>
          </form>
        </div>


        <div className="premium-card rounded-[2rem] p-5 md:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 className="font-semibold text-white">
                MT5 Accounts
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Accounts validated through your MT5 terminal.
              </p>
            </div>

            <button
              type="button"
              disabled={
                syncMutation.isPending ||
                accounts.length === 0
              }
              onClick={() =>
                syncMutation.mutate()
              }
              className="flex items-center justify-center gap-2 rounded-2xl border border-white/10 px-4 py-2.5 text-sm font-medium text-slate-200 transition hover:bg-white/[0.05] disabled:cursor-not-allowed disabled:opacity-40"
            >
              {syncMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}

              Sync Trades
            </button>
          </div>


          {accountsQuery.isLoading ? (
            <div className="flex min-h-52 items-center justify-center">
              <Loader2 className="h-6 w-6 animate-spin text-blue-300" />
            </div>
          ) : null}


          {accountsQuery.isError ? (
            <div className="mt-5 rounded-2xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-200">
              Unable to load MT5 accounts.
            </div>
          ) : null}


          {!accountsQuery.isLoading &&
          !accountsQuery.isError &&
          accounts.length === 0 ? (
            <div className="mt-5 rounded-3xl border border-dashed border-white/10 p-8 text-center">
              <Server className="mx-auto h-7 w-7 text-slate-500" />

              <p className="mt-3 font-medium text-white">
                No MT5 account linked
              </p>

              <p className="mt-2 text-sm text-slate-500">
                Connect an account to begin syncing trades and
                assigning your Strategy Brain strategy.
              </p>
            </div>
          ) : null}


          <div className="mt-5 space-y-4">
            {accounts.map(
              (
                account:
                  MT5BrokerAccount,
              ) => {
                const linked =
                  account
                    .strategy_profile_id
                    ? strategyById.get(
                        account
                          .strategy_profile_id,
                      )
                    : undefined

                const selected =
                  selectedStrategies[
                    account.id
                  ] ||
                  (
                    account
                      .strategy_profile_id
                      ? String(
                          account
                            .strategy_profile_id,
                        )
                      : ""
                  )

                return (
                  <article
                    key={
                      account.id
                    }
                    className="rounded-3xl border border-white/10 bg-black/10 p-5"
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-semibold text-white">
                            {account.broker}
                          </h3>

                          <span className="flex items-center gap-1 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 text-[11px] font-medium text-emerald-300">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            Account linked
                          </span>
                        </div>

                        <p className="mt-2 text-sm text-slate-400">
                          {account.server}
                        </p>

                        <p className="mt-1 font-mono text-xs text-slate-500">
                          Account {account.account_number}
                        </p>
                      </div>

                      <button
                        type="button"
                        disabled={
                          removeMutation.isPending
                        }
                        onClick={() => {
                          const confirmed =
                            window.confirm(
                              "Remove this MT5 account from TradePilotAI?",
                            )

                          if (
                            confirmed
                          ) {
                            removeMutation.mutate(
                              account.id,
                            )
                          }
                        }}
                        className="flex items-center gap-2 self-start rounded-xl border border-red-400/20 px-3 py-2 text-xs text-red-300 transition hover:bg-red-400/10"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Remove
                      </button>
                    </div>

                    <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
                      <Clock3 className="h-3.5 w-3.5" />
                      Last sync:
                      {" "}
                      {formatLastSync(
                        account.last_sync,
                      )}
                    </div>


                    <div className="mt-5 border-t border-white/10 pt-5">
                      <div className="flex items-center gap-2">
                        <BrainCircuit className="h-4 w-4 text-violet-300" />

                        <p className="text-sm font-medium text-white">
                          Strategy Brain
                        </p>
                      </div>

                      <div className="mt-3 flex flex-col gap-3 sm:flex-row">
                        <select
                          value={
                            selected
                          }
                          onChange={(event) =>
                            setSelectedStrategies(
                              (
                                current,
                              ) => ({
                                ...current,
                                [
                                  account.id
                                ]:
                                  event
                                    .target
                                    .value,
                              }),
                            )
                          }
                          className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-blue-400/50"
                        >
                          <option value="">
                            Select active strategy
                          </option>

                          {activeStrategies.map(
                            (
                              strategy,
                            ) => (
                              <option
                                key={
                                  strategy.id
                                }
                                value={
                                  strategy.id
                                }
                              >
                                {
                                  strategy.name
                                }
                              </option>
                            ),
                          )}
                        </select>

                        <button
                          type="button"
                          disabled={
                            !selected ||
                            linkMutation.isPending
                          }
                          onClick={() =>
                            linkMutation.mutate(
                              {
                                accountId:
                                  account.id,

                                strategyId:
                                  Number(
                                    selected,
                                  ),
                              },
                            )
                          }
                          className="rounded-2xl bg-violet-500/15 px-4 py-3 text-sm font-medium text-violet-200 transition hover:bg-violet-500/25 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                          Link Strategy
                        </button>

                        {account.strategy_profile_id ? (
                          <button
                            type="button"
                            disabled={
                              unlinkMutation.isPending
                            }
                            onClick={() =>
                              unlinkMutation.mutate(
                                account.id,
                              )
                            }
                            className="flex items-center justify-center gap-2 rounded-2xl border border-white/10 px-4 py-3 text-sm text-slate-300 transition hover:bg-white/[0.04]"
                          >
                            <Unplug className="h-4 w-4" />
                            Unlink
                          </button>
                        ) : null}
                      </div>

                      {linked ? (
                        <StrategyDetails
                          strategy={
                            linked
                          }
                        />
                      ) : (
                        <p className="mt-4 text-sm leading-6 text-slate-500">
                          No Strategy Brain strategy is linked to
                          this MT5 account. AutoTrader will not be
                          allowed to operate without one.
                        </p>
                      )}
                    </div>


                    <div className="mt-5 border-t border-white/10 pt-5">
                      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                        <div className="max-w-xl">
                          <div className="flex flex-wrap items-center gap-2">
                            <Bot className="h-4 w-4 text-amber-300" />

                            <p className="text-sm font-medium text-white">
                              AutoTrader
                            </p>

                            <span
                              className={
                                account.autotrader_enabled
                                  ? "rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-300"
                                  : "rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[11px] font-semibold text-slate-400"
                              }
                            >
                              {account.autotrader_enabled
                                ? "ON"
                                : "OFF"}
                            </span>
                          </div>

                          <p className="mt-2 text-xs leading-5 text-slate-500">
                            Monitors forex markets using this account's linked
                            Strategy Brain strategy. Every live trade will
                            still require your explicit approval.
                          </p>
                        </div>

                        <div className="flex flex-col gap-2 sm:flex-row">
                          <select
                            value={
                              autoTraderHoldMinutes[
                                account.id
                              ] ??
                              (
                                account.max_hold_minutes === 60
                                  ? 60
                                  : 30
                              )
                            }
                            disabled={
                              account.autotrader_enabled ||
                              enableAutoTraderMutation.isPending ||
                              disableAutoTraderMutation.isPending
                            }
                            onChange={(event) =>
                              setAutoTraderHoldMinutes(
                                (current) => ({
                                  ...current,
                                  [account.id]:
                                    Number(
                                      event.target.value,
                                    ) === 60
                                      ? 60
                                      : 30,
                                }),
                              )
                            }
                            className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-amber-400/50 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            <option value={30}>
                              Max hold: 30 min
                            </option>

                            <option value={60}>
                              Max hold: 60 min
                            </option>
                          </select>

                          {account.autotrader_enabled ? (
                            <button
                              type="button"
                              disabled={
                                disableAutoTraderMutation.isPending
                              }
                              onClick={() =>
                                disableAutoTraderMutation.mutate(
                                  account.id,
                                )
                              }
                              className="flex items-center justify-center gap-2 rounded-2xl border border-red-400/20 px-4 py-3 text-sm font-medium text-red-300 transition hover:bg-red-400/10 disabled:cursor-not-allowed disabled:opacity-40"
                            >
                              {disableAutoTraderMutation.isPending ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Unplug className="h-4 w-4" />
                              )}

                              Disable AutoTrader
                            </button>
                          ) : (
                            <button
                              type="button"
                              disabled={
                                !account.strategy_profile_id ||
                                enableAutoTraderMutation.isPending
                              }
                              onClick={() =>
                                enableAutoTraderMutation.mutate({
                                  accountId:
                                    account.id,

                                  maxHoldMinutes:
                                    autoTraderHoldMinutes[
                                      account.id
                                    ] ??
                                    (
                                      account.max_hold_minutes === 60
                                        ? 60
                                        : 30
                                    ),
                                })
                              }
                              className="flex items-center justify-center gap-2 rounded-2xl bg-amber-400/15 px-4 py-3 text-sm font-medium text-amber-200 transition hover:bg-amber-400/25 disabled:cursor-not-allowed disabled:opacity-40"
                            >
                              {enableAutoTraderMutation.isPending ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Bot className="h-4 w-4" />
                              )}

                              Enable AutoTrader
                            </button>
                          )}
                        </div>
                      </div>

                      {!account.strategy_profile_id ? (
                        <p className="mt-3 text-xs text-amber-200/70">
                          Link an active Strategy Brain strategy before
                          enabling AutoTrader.
                        </p>
                      ) : null}

                      {account.autotrader_enabled ? (
                        <div className="mt-4 rounded-2xl border border-emerald-400/15 bg-emerald-400/[0.05] p-4">
                          <div className="flex items-center gap-2 text-xs font-medium text-emerald-200">
                            <ShieldCheck className="h-4 w-4" />
                            Monitoring enabled
                          </div>

                          <p className="mt-2 text-xs leading-5 text-slate-400">
                            Maximum holding window:
                            {" "}
                            {account.max_hold_minutes}
                            {" "}
                            minutes. AutoTrader cannot place a live order
                            without trader approval.
                          </p>
                        </div>
                      ) : null}
                    </div>
                  </article>
                )
              },
            )}
          </div>
        </div>
      </section>


      <section className="premium-card rounded-[2rem] p-5 md:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm font-medium text-amber-300">
              <Clock3 className="h-4 w-4" />
              Approval Center
            </div>

            <h2 className="mt-2 text-xl font-semibold text-white">
              Pending Trade Approvals
            </h2>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              AutoTrader can prepare Forex trade proposals from
              your linked Strategy Brain strategy, but no live
              MT5 order can be placed until you explicitly
              approve the trade.
            </p>
          </div>

          <div className="self-start rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1.5 text-xs font-medium text-amber-200">
            {pendingProposals.length}
            {" "}
            pending
          </div>
        </div>


        {pendingProposalsQuery.isLoading ? (
          <div className="flex min-h-40 items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-amber-300" />
          </div>
        ) : null}


        {pendingProposalsQuery.isError ? (
          <div className="mt-5 rounded-2xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-200">
            Unable to load pending trade approvals.
          </div>
        ) : null}


        {!pendingProposalsQuery.isLoading &&
        !pendingProposalsQuery.isError &&
        pendingProposals.length === 0 ? (
          <div className="mt-6 rounded-3xl border border-dashed border-white/10 p-8 text-center">
            <ShieldCheck className="mx-auto h-8 w-8 text-slate-500" />

            <p className="mt-3 font-medium text-white">
              No trades waiting for approval
            </p>

            <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-500">
              When AutoTrader identifies a valid Forex setup
              that satisfies your Strategy Brain rules, it will
              appear here for review.
            </p>
          </div>
        ) : null}


        <div className="mt-6 space-y-5">
          {pendingProposals.map(
            (proposal) => {
              const account =
                accounts.find(
                  (item) =>
                    item.id ===
                    proposal.broker_account_id,
                )

              const strategy =
                proposal.strategy_profile_id
                  ? strategyById.get(
                      proposal.strategy_profile_id,
                    )
                  : undefined

              const timeRemaining =
                proposalTimeRemaining(
                  proposal.expires_at,
                  nowMs,
                )

              const isExpired =
                timeRemaining ===
                "Expired"

              const direction =
                proposal.direction
                  .trim()
                  .toUpperCase()

              const matchedRules =
                proposal.matched_rules || []

              const timeframeEntries =
                Object.entries(
                  proposal.timeframe_context || {},
                )

              const mutationBusy =
                approveProposalMutation.isPending ||
                rejectProposalMutation.isPending

              return (
                <article
                  key={proposal.id}
                  className="rounded-3xl border border-amber-400/15 bg-amber-400/[0.03] p-5 md:p-6"
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={
                            direction === "BUY"
                              ? "rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300"
                              : "rounded-full border border-red-400/20 bg-red-400/10 px-3 py-1 text-xs font-semibold text-red-300"
                          }
                        >
                          {direction}
                        </span>

                        <h3 className="text-xl font-semibold text-white">
                          {proposal.symbol}
                        </h3>

                        <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[11px] text-slate-400">
                          Proposal #{proposal.id}
                        </span>
                      </div>

                      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-400">
                        <span>
                          Broker:
                          {" "}
                          {account?.broker ||
                            "MT5"}
                        </span>

                        <span>
                          Strategy:
                          {" "}
                          {strategy?.name ||
                            "Strategy Brain"}
                        </span>

                        <span>
                          Max hold:
                          {" "}
                          {proposal.max_hold_minutes}
                          {" "}
                          min
                        </span>
                      </div>
                    </div>

                    <div
                      className={
                        isExpired
                          ? "flex items-center gap-2 self-start rounded-full border border-red-400/20 bg-red-400/10 px-3 py-2 text-xs font-medium text-red-300"
                          : "flex items-center gap-2 self-start rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs font-medium text-amber-200"
                      }
                    >
                      <Clock3 className="h-4 w-4" />

                      {isExpired
                        ? "Expired"
                        : `Expires in ${timeRemaining}`}
                    </div>
                  </div>


                  {proposal.analysis_summary ? (
                    <div className="mt-5 rounded-2xl border border-white/10 bg-black/10 p-4">
                      <div className="flex items-center gap-2 text-xs font-medium text-blue-300">
                        <BrainCircuit className="h-4 w-4" />
                        Strategy Analysis
                      </div>

                      <p className="mt-2 text-sm leading-6 text-slate-300">
                        {proposal.analysis_summary}
                      </p>
                    </div>
                  ) : null}


                  <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                    <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                      <p className="text-xs text-slate-500">
                        Entry
                      </p>

                      <p className="mt-1 font-mono font-semibold text-white">
                        {formatProposalPrice(
                          proposal.entry_price,
                        )}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                      <p className="text-xs text-slate-500">
                        Stop Loss
                      </p>

                      <p className="mt-1 font-mono font-semibold text-red-300">
                        {formatProposalPrice(
                          proposal.stop_loss,
                        )}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                      <p className="text-xs text-slate-500">
                        Take Profit
                      </p>

                      <p className="mt-1 font-mono font-semibold text-emerald-300">
                        {formatProposalPrice(
                          proposal.take_profit,
                        )}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                      <p className="text-xs text-slate-500">
                        Risk
                      </p>

                      <p className="mt-1 font-semibold text-white">
                        {proposal.risk_percent}%
                      </p>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                      <p className="text-xs text-slate-500">
                        Risk / Reward
                      </p>

                      <p className="mt-1 font-semibold text-white">
                        1:
                        {proposal.risk_reward}
                      </p>
                    </div>
                  </div>


                  {timeframeEntries.length > 0 ? (
                    <div className="mt-5">
                      <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                        Timeframe Analysis
                      </p>

                      <div className="mt-3 flex flex-wrap gap-2">
                        {timeframeEntries
                          .slice(0, 8)
                          .map(
                            ([
                              timeframe,
                              value,
                            ]) => (
                              <span
                                key={timeframe}
                                className="rounded-full border border-blue-400/15 bg-blue-400/[0.06] px-3 py-1.5 text-xs text-blue-200"
                              >
                                {timeframe}
                                {": "}
                                {typeof value ===
                                "string"
                                  ? value
                                  : JSON.stringify(
                                      value,
                                    )}
                              </span>
                            ),
                          )}
                      </div>
                    </div>
                  ) : null}


                  {matchedRules.length > 0 ? (
                    <div className="mt-5">
                      <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                        Strategy Brain Rules Matched
                      </p>

                      <div className="mt-3 grid gap-2 md:grid-cols-2">
                        {matchedRules
                          .slice(0, 8)
                          .map(
                            (
                              rule,
                              index,
                            ) => (
                              <div
                                key={`${proposal.id}-rule-${index}`}
                                className="flex items-start gap-2 rounded-2xl border border-emerald-400/10 bg-emerald-400/[0.04] p-3 text-xs leading-5 text-slate-300"
                              >
                                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" />

                                <span>
                                  {proposalRuleLabel(
                                    rule,
                                  )}
                                </span>
                              </div>
                            ),
                          )}
                      </div>
                    </div>
                  ) : null}


                  <div className="mt-6 rounded-2xl border border-amber-400/15 bg-amber-400/[0.04] p-4">
                    <div className="flex items-start gap-3">
                      <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />

                      <p className="text-xs leading-5 text-slate-400">
                        Approval authorizes TradePilot to record
                        your decision only at this stage. Live
                        MT5 order execution has not been enabled
                        yet and this button does not send an
                        order to your broker.
                      </p>
                    </div>
                  </div>


                  <div className="mt-5 grid gap-3 sm:grid-cols-2">
                    <button
                      type="button"
                      disabled={
                        mutationBusy ||
                        isExpired
                      }
                      onClick={() => {
                        const confirmed =
                          window.confirm(
                            `Reject ${proposal.symbol} ${direction} trade proposal?`,
                          )

                        if (confirmed) {
                          rejectProposalMutation.mutate(
                            proposal.id,
                          )
                        }
                      }}
                      className="flex items-center justify-center gap-2 rounded-2xl border border-red-400/20 px-4 py-3 text-sm font-semibold text-red-300 transition hover:bg-red-400/10 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      {rejectProposalMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}

                      Reject Trade
                    </button>

                    <button
                      type="button"
                      disabled={
                        mutationBusy ||
                        isExpired
                      }
                      onClick={() => {
                        const confirmed =
                          window.confirm(
                            `Approve ${proposal.symbol} ${direction} at ${formatProposalPrice(proposal.entry_price)} with SL ${formatProposalPrice(proposal.stop_loss)} and TP ${formatProposalPrice(proposal.take_profit)}?`,
                          )

                        if (confirmed) {
                          approveProposalMutation.mutate(
                            proposal.id,
                          )
                        }
                      }}
                      className="flex items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      {approveProposalMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <ShieldCheck className="h-4 w-4" />
                      )}

                      Approve Trade
                    </button>
                  </div>
                </article>
              )
            },
          )}
        </div>
      </section>


    </div>
  )
}






