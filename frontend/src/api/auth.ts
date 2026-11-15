import axios from "axios"

import api from "@/api/client"

export type AuthChallenge = {
  status: "otp_required"
  challenge_id: string
  email_hint: string
  expires_in: number
  resend_in?: number
}

export type TokenResponse = {
  access_token: string
  token_type?: string
}

export type StartResult =
  | { kind: "code"; challenge: AuthChallenge }
  | { kind: "token"; token: TokenResponse }

function isChallenge(data: unknown): data is AuthChallenge {
  const value = data as Partial<AuthChallenge> | null

  return (
    !!value &&
    value.status === "otp_required" &&
    typeof value.challenge_id === "string"
  )
}

function isToken(data: unknown): data is TokenResponse {
  const value = data as Partial<TokenResponse> | null

  return !!value && typeof value.access_token === "string"
}

export async function startLogin(
  email: string,
  password: string,
): Promise<StartResult> {
  const form = new URLSearchParams()

  form.set("username", email.trim().toLowerCase())
  form.set("password", password)

  const { data } = await api.post("/auth/login", form, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  })

  if (isChallenge(data)) {
    return { kind: "code", challenge: data }
  }

  // Older servers return the token straight away. Once every server asks
  // for the emailed code, this branch can be deleted.
  if (isToken(data)) {
    return { kind: "token", token: data }
  }

  throw new Error("Unexpected sign-in response.")
}

export async function registerAccount(input: {
  fullName: string
  email: string
  password: string
}): Promise<StartResult> {
  const email = input.email.trim().toLowerCase()

  const { data } = await api.post("/auth/register", {
    email,
    password: input.password,
    full_name: input.fullName.trim() || null,
    accept_terms: true,
  })

  if (isChallenge(data)) {
    return { kind: "code", challenge: data }
  }

  const legacy = data as { error?: string; user_id?: number } | null

  if (legacy?.error) {
    throw new Error(legacy.error)
  }

  // Older servers create the account and expect a separate sign-in.
  if (legacy?.user_id) {
    return startLogin(email, input.password)
  }

  throw new Error("Account could not be created.")
}

export async function verifyLoginCode(
  challengeId: string,
  code: string,
): Promise<TokenResponse> {
  const { data } = await api.post("/auth/login/verify", {
    challenge_id: challengeId,
    code,
  })

  if (!isToken(data)) {
    throw new Error("Unexpected verification response.")
  }

  return data
}

export async function resendLoginCode(
  challengeId: string,
): Promise<{ resend_in: number }> {
  const { data } = await api.post("/auth/login/resend", {
    challenge_id: challengeId,
  })

  return { resend_in: Number(data?.resend_in) || 60 }
}

export async function requestPasswordReset(email: string): Promise<void> {
  await api.post("/auth/password/forgot", {
    email: email.trim().toLowerCase(),
  })
}

export async function resetPassword(
  token: string,
  newPassword: string,
): Promise<void> {
  await api.post("/auth/password/reset", {
    token,
    new_password: newPassword,
  })
}

type ErrorDetail = {
  code?: string
  message?: string
}

function detailOf(error: unknown): unknown {
  return axios.isAxiosError(error)
    ? error.response?.data?.detail
    : undefined
}

export function errorCode(error: unknown): string | undefined {
  const detail = detailOf(error) as ErrorDetail | string | undefined

  return typeof detail === "object" && detail !== null
    ? detail.code
    : undefined
}

export function errorMessage(error: unknown, fallback: string): string {
  const detail = detailOf(error)

  if (typeof detail === "string" && detail) {
    return detail
  }

  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    const message = (detail as ErrorDetail).message

    if (message) {
      return message
    }
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string }

    if (first?.msg) {
      return first.msg
    }
  }

  if (axios.isAxiosError(error)) {
    if (error.response?.status === 429) {
      return "Too many attempts. Please wait a few minutes and try again."
    }

    if (!error.response) {
      return "Cannot reach the server. Check your connection and try again."
    }
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}
