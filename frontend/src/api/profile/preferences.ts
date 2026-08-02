import { api } from "@/api"
import type { AuthUser } from "@/types"

export type UserPreferences = {
  preferred_language: string
  preferred_currency: string
}

export async function updatePreferences(
  preferences: UserPreferences,
): Promise<AuthUser> {
  const response =
    await api.put<AuthUser>(
      "/profile",
      preferences,
    )

  return response.data
}
