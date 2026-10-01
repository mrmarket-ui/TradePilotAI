import api from "@/api/client"


export type MT5BrokerAccount = {
  id: number
  broker: string
  server: string
  account_number: string
  connected: boolean
  last_sync: string | null
  strategy_profile_id: number | null
  autotrader_enabled: boolean
  max_hold_minutes: number
}


export type ConnectMT5Payload = {
  broker: string
  server: string
  account_number: number
  password: string
}


export type MT5SyncResponse = {
  accounts: number
  synced_accounts: number
  failed_accounts: Array<{
    account_id: number
    message: string
  }>
  imported: number
  skipped: number
  status: "success" | "partial"
}


export type MT5ProposalStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "expired"
  | "executed"
  | "failed"


export type MT5TradeProposal = {
  id: number
  user_id: number

  broker_account_id: number
  strategy_profile_id: number | null

  symbol: string
  direction: string

  entry_price: number
  stop_loss: number
  take_profit: number

  risk_percent: number
  risk_reward: number

  max_hold_minutes: number

  timeframe_context:
    | Record<string, unknown>
    | null

  matched_rules:
    | unknown[]
    | null

  missing_rules:
    | unknown[]
    | null

  strategy_snapshot:
    | Record<string, unknown>
    | null

  analysis_summary:
    | string
    | null

  status: MT5ProposalStatus

  expires_at: string
  approved_at: string | null
  rejected_at: string | null
  executed_at: string | null

  created_at: string
  updated_at: string
}


export async function getMT5Accounts():
  Promise<MT5BrokerAccount[]> {
  const response =
    await api.get<MT5BrokerAccount[]>(
      "/brokers",
    )

  return response.data
}


export async function connectMT5Account(
  payload: ConnectMT5Payload,
): Promise<MT5BrokerAccount> {
  const response =
    await api.post<MT5BrokerAccount>(
      "/brokers/connect",
      payload,
    )

  return response.data
}


export async function linkMT5Strategy(
  accountId: number,
  strategyProfileId: number,
): Promise<MT5BrokerAccount> {
  const response =
    await api.patch<MT5BrokerAccount>(
      `/brokers/${accountId}/strategy`,
      {
        strategy_profile_id:
          strategyProfileId,
      },
    )

  return response.data
}


export async function unlinkMT5Strategy(
  accountId: number,
): Promise<MT5BrokerAccount> {
  const response =
    await api.delete<MT5BrokerAccount>(
      `/brokers/${accountId}/strategy`,
    )

  return response.data
}


export async function enableMT5AutoTrader(
  accountId: number,
  maxHoldMinutes: 30 | 60,
): Promise<MT5BrokerAccount> {
  const response =
    await api.post<MT5BrokerAccount>(
      `/brokers/${accountId}/autotrader/enable`,
      {
        max_hold_minutes: maxHoldMinutes,
      },
    )

  return response.data
}


export async function disableMT5AutoTrader(
  accountId: number,
): Promise<MT5BrokerAccount> {
  const response =
    await api.post<MT5BrokerAccount>(
      `/brokers/${accountId}/autotrader/disable`,
    )

  return response.data
}


export async function removeMT5Account(
  accountId: number,
): Promise<void> {
  await api.delete(
    `/brokers/${accountId}`,
  )
}


export async function syncMT5Trades():
  Promise<MT5SyncResponse> {
  const response =
    await api.post<MT5SyncResponse>(
      "/trading/sync",
    )

  return response.data
}

export async function getMT5Proposals(
  proposalStatus?: MT5ProposalStatus,
): Promise<MT5TradeProposal[]> {
  const response =
    await api.get<MT5TradeProposal[]>(
      "/mt5/proposals",
      {
        params:
          proposalStatus
            ? {
                status:
                  proposalStatus,
              }
            : undefined,
      },
    )

  return response.data
}


export async function getMT5Proposal(
  proposalId: number,
): Promise<MT5TradeProposal> {
  const response =
    await api.get<MT5TradeProposal>(
      `/mt5/proposals/${proposalId}`,
    )

  return response.data
}


export async function approveMT5Proposal(
  proposalId: number,
): Promise<MT5TradeProposal> {
  const response =
    await api.post<MT5TradeProposal>(
      `/mt5/proposals/${proposalId}/approve`,
    )

  return response.data
}


export async function rejectMT5Proposal(
  proposalId: number,
): Promise<MT5TradeProposal> {
  const response =
    await api.post<MT5TradeProposal>(
      `/mt5/proposals/${proposalId}/reject`,
    )

  return response.data
}

