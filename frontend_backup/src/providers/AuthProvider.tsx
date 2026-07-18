import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react"
import { loadCurrentUser, loginUser } from "@/api/auth"
import type { AuthUser, LoginCredentials } from "@/types/auth"

type AuthContextValue = {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function readStoredUser(): AuthUser | null {
  const stored = localStorage.getItem("tradepilot_user")
  if (!stored) return null
  try { return JSON.parse(stored) }
  catch { localStorage.removeItem("tradepilot_user"); return null }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("tradepilot_access_token"))
  const [user, setUser] = useState<AuthUser | null>(readStoredUser)
  const [isLoading, setIsLoading] = useState(Boolean(token))

  const logout = useCallback(() => {
    localStorage.removeItem("tradepilot_access_token")
    localStorage.removeItem("tradepilot_user")
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    if (!token) { setIsLoading(false); return }
    let active = true
    ;(async () => {
      try {
        const currentUser = await loadCurrentUser()
        if (active && currentUser) {
          setUser(currentUser)
          localStorage.setItem("tradepilot_user", JSON.stringify(currentUser))
        }
      } catch {
        if (active) logout()
      } finally {
        if (active) setIsLoading(false)
      }
    })()
    return () => { active = false }
  }, [token, logout])

  const login = useCallback(async (credentials: LoginCredentials) => {
    const response = await loginUser(credentials)
    const accessToken = response.access_token as string
    localStorage.setItem("tradepilot_access_token", accessToken)
    setToken(accessToken)
    const currentUser = response.user || await loadCurrentUser().catch(() => null) || { email: credentials.email }
    localStorage.setItem("tradepilot_user", JSON.stringify(currentUser))
    setUser(currentUser)
  }, [])

  const value = useMemo(() => ({ user, token, isAuthenticated: Boolean(token), isLoading, login, logout }), [user, token, isLoading, login, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth must be used inside AuthProvider.")
  return context
}
