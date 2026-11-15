import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"

import { me } from "@/api"
import type { AuthUser, LoginCredentials } from "@/types"

type AuthValue = {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  /** Direct sign-in is retired: every sign-in now goes through the emailed code. */
  login: (credentials: LoginCredentials) => Promise<void>
  /** Called once the emailed code has been verified and a token was issued. */
  completeLogin: (accessToken: string) => Promise<void>
  logout: () => void
}

const TOKEN_KEY = "tradepilot_access_token"
const USER_KEY = "tradepilot_user"

const AuthContext = createContext<AuthValue | null>(null)

function readStoredUser(): AuthUser | null {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || "null")
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<AuthUser | null>(readStoredUser)
  const [isLoading, setLoading] = useState(Boolean(token))

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }

    let active = true

    ;(async () => {
      try {
        const profile = await me()

        if (active && profile) {
          setUser(profile)
          localStorage.setItem(USER_KEY, JSON.stringify(profile))
        }
      } catch {
        if (active) {
          logout()
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    })()

    return () => {
      active = false
    }
  }, [token, logout])

  const login = useCallback(async (_credentials: LoginCredentials) => {
    throw new Error("Sign-in now requires the emailed verification code.")
  }, [])

  const completeLogin = useCallback(
    async (accessToken: string) => {
      localStorage.setItem(TOKEN_KEY, accessToken)

      try {
        const profile = await me()

        if (!profile) {
          throw new Error("Could not load your profile.")
        }

        localStorage.setItem(USER_KEY, JSON.stringify(profile))
        setUser(profile)
        setToken(accessToken)
      } catch (error) {
        logout()
        throw error
      }
    },
    [logout],
  )

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(token),
      isLoading,
      login,
      completeLogin,
      logout,
    }),
    [user, token, isLoading, login, completeLogin, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const value = useContext(AuthContext)

  if (!value) {
    throw new Error("useAuth outside provider")
  }

  return value
}
