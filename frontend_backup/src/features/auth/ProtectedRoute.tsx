import { Navigate, Outlet, useLocation } from "react-router-dom"
import { useAuth } from "@/providers/AuthProvider"

export default function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()
  if (isLoading) return <div className="grid min-h-screen place-items-center bg-[#060912]"><div className="text-center"><div className="mx-auto size-10 animate-spin rounded-full border-2 border-blue-400/20 border-t-blue-400"/><p className="mt-4 text-sm text-slate-400">Securing your workspace...</p></div></div>
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  return <Outlet />
}
