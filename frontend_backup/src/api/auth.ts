import axios from "axios"
import api from "@/api/client"
import type { LoginCredentials, LoginResponse } from "@/types/auth"

function tokenFrom(data: LoginResponse) {
  const token = data.access_token || data.token
  if (!token) throw new Error("The backend did not return an access token.")
  return token
}

export async function loginUser(credentials: LoginCredentials): Promise<LoginResponse> {
  try {
    const response = await api.post<LoginResponse>("/auth/login", credentials)
    return { ...response.data, access_token: tokenFrom(response.data) }
  } catch (error) {
    if (!axios.isAxiosError(error) || error.response?.status !== 422) throw error
    const form = new URLSearchParams()
    form.set("username", credentials.email)
    form.set("password", credentials.password)
    const response = await api.post<LoginResponse>("/auth/login", form, { headers: { "Content-Type": "application/x-www-form-urlencoded" } })
    return { ...response.data, access_token: tokenFrom(response.data) }
  }
}

export async function loadCurrentUser() {
  for (const path of ["/auth/me", "/profile/me", "/users/me"]) {
    try { return (await api.get(path)).data }
    catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) continue
      throw error
    }
  }
  return null
}
