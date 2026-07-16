export type LoginCredentials = { email: string; password: string }
export type AuthUser = { id?: number; email: string; full_name?: string; username?: string }
export type LoginResponse = { access_token?: string; token?: string; token_type?: string; user?: AuthUser }
