import {
  Navigate,
  Outlet,
  Route,
  Routes,
} from "react-router-dom"

import { useAuth } from "@/Auth"
import Shell from "@/Shell"

import {
  Analytics,
  Billing,
  Coach,
  DNA,
  Login,
  Reports,
  Settings,
  Trades,
} from "@/pages"

import DashboardPage from "@/pages/DashboardPage"
import StrategyLabPage from "@/pages/StrategyLabPage"
import SetupScorerPage from "@/pages/SetupScorerPage"
import PartnersPage from "@/pages/PartnersPage"
import PartnerDetailPage from "@/pages/PartnerDetailPage"
import PartnerComparePage from "@/pages/PartnerComparePage"
import PartnerMatchPage from "@/pages/PartnerMatchPage"

import AdminLayout from "@/pages/admin/AdminLayout"
import AdminDashboard from "@/pages/admin/AdminDashboard"
import AdminUsers from "@/pages/admin/AdminUsers"
import AdminSubscriptions from "@/pages/admin/AdminSubscriptions"
import AdminSystem from "@/pages/admin/AdminSystem"
import AdminPartners from "@/pages/admin/AdminPartners"
import AdminPartnerAnalytics from "@/pages/admin/AdminPartnerAnalytics"
import AdminPartnerOffers from "@/pages/admin/AdminPartnerOffers"


function LoadingScreen({
  message = "Loading...",
}: {
  message?: string
}) {
  return (
    <div className="grid min-h-[50vh] place-items-center text-slate-400">
      {message}
    </div>
  )
}


function Protected() {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth()

  if (isLoading) {
    return (
      <LoadingScreen />
    )
  }

  return isAuthenticated ? (
    <Shell />
  ) : (
    <Navigate
      to="/login"
      replace
    />
  )
}


function PaidProtected() {
  const {
    user,
    isLoading,
  } = useAuth()

  if (isLoading) {
    return (
      <LoadingScreen
        message="Checking subscription..."
      />
    )
  }

  if (user?.is_admin) {
    return <Outlet />
  }

  const plan =
    user?.plan?.toLowerCase() ||
    "free"

  if (
    plan !== "pro" &&
    plan !== "premium"
  ) {
    return (
      <Navigate
        to="/billing"
        replace
      />
    )
  }

  return <Outlet />
}


function PremiumProtected() {
  const {
    user,
    isLoading,
  } = useAuth()

  if (isLoading) {
    return (
      <LoadingScreen
        message="Checking Premium access..."
      />
    )
  }

  // Owner/admin always receives full access.
  if (user?.is_admin) {
    return <Outlet />
  }

  if (
    user?.plan?.toLowerCase()
    !== "premium"
  ) {
    return (
      <Navigate
        to="/billing"
        replace
      />
    )
  }

  return <Outlet />
}


function AdminProtected() {
  const {
    user,
    isLoading,
  } = useAuth()

  if (isLoading) {
    return (
      <LoadingScreen
        message="Checking administrator access..."
      />
    )
  }

  if (!user?.is_admin) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  return <Outlet />
}


export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<Login />}
      />

      <Route element={<Protected />}>
        {/* FREE */}
        <Route
          path="/dashboard"
          element={<DashboardPage />}
        />

        <Route
          path="/trades"
          element={<Trades />}
        />

        <Route
          path="/partners"
          element={<PartnersPage />}
        />

        <Route
          path="/billing"
          element={<Billing />}
        />

        <Route
          path="/settings"
          element={<Settings />}
        />

        {/* PRO + PREMIUM + ADMIN */}
        <Route element={<PaidProtected />}>
          <Route
            path="/analytics"
            element={<Analytics />}
          />

          <Route
            path="/trader-dna"
            element={<DNA />}
          />

          <Route
            path="/coach"
            element={<Coach />}
          />

          <Route
            path="/reports"
            element={<Reports />}
          />
        </Route>

        {/* PREMIUM + ADMIN */}
        <Route element={<PremiumProtected />}>
          <Route
            path="/strategy-lab"
            element={<StrategyLabPage />}
          />

          <Route
            path="/setup-scorer"
            element={<SetupScorerPage />}
          />
        </Route>

        {/* ADMIN ONLY */}
        <Route element={<AdminProtected />}>
          <Route
            path="/admin"
            element={<AdminLayout />}
          >
            <Route
              index
              element={<AdminDashboard />}
            />

            <Route
              path="users"
              element={<AdminUsers />}
            />

            <Route
              path="subscriptions"
              element={<AdminSubscriptions />}
            />

            <Route
              path="partners"
              element={<AdminPartners />}
            />
            <Route
              path="partner-analytics"
              element={<AdminPartnerAnalytics />}
            />
            <Route
              path="partner-offers"
              element={<AdminPartnerOffers />}
            />

            <Route
              path="system"
              element={<AdminSystem />}
            />
          </Route>
        </Route>
      </Route>

      <Route
        path="*"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />
    </Routes>
  )
}






