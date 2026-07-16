import { Navigate, Route, Routes } from "react-router-dom"
import ProtectedRoute from "@/features/auth/ProtectedRoute"
import AppLayout from "@/layouts/AppLayout"
import DashboardPage from "@/pages/DashboardPage"
import LoginPage from "@/pages/LoginPage"
import PlaceholderPage from "@/pages/PlaceholderPage"

export default function App() {
  return <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route element={<ProtectedRoute />}>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/trades" element={<PlaceholderPage title="Trade Journal" />} />
        <Route path="/analytics" element={<PlaceholderPage title="Analytics" />} />
        <Route path="/trader-dna" element={<PlaceholderPage title="Trader DNA" />} />
        <Route path="/coach" element={<PlaceholderPage title="AI Coach" />} />
        <Route path="/reports" element={<PlaceholderPage title="Reports" />} />
        <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to="/dashboard" replace />} />
  </Routes>
}
