import {
  BarChart3,
  BrainCircuit,
  Cable,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Sparkles,
  WalletCards,
  X,
} from "lucide-react"
import {
  useEffect,
  useMemo,
  useState,
} from "react"
import { useNavigate } from "react-router-dom"

type OnboardingTourProps = {
  userId?: number | string | null
  plan?: string | null
  isAdmin?: boolean
}

type TourStep = {
  title: string
  eyebrow: string
  description: string
  details: string[]
  path?: string
  action?: string
  premium?: boolean
  icon: typeof LayoutDashboard
}

export const ONBOARDING_REPLAY_EVENT =
  "tradepilot:replay-onboarding"

function storageKey(
  userId?: number | string | null,
) {
  return userId
    ? `tradepilot_onboarding_complete_${userId}`
    : "tradepilot_onboarding_complete"
}

export default function OnboardingTour({
  userId,
  plan,
  isAdmin = false,
}: OnboardingTourProps) {
  const navigate = useNavigate()

  const [
    isOpen,
    setIsOpen,
  ] = useState(false)

  const [
    stepIndex,
    setStepIndex,
  ] = useState(0)

  const normalizedPlan =
    plan?.toLowerCase() || "free"

  const hasPremium =
    isAdmin ||
    normalizedPlan === "premium"

  const steps =
    useMemo<TourStep[]>(
      () => [
        {
          eyebrow: "Welcome",
          title: "Welcome to TradePilot AI",
          description:
            "Your trading workspace for journaling, strategy development, performance analysis and smarter decision-making.",
          details: [
            "Track your trading activity in one place.",
            "Build discipline around a defined trading strategy.",
            "Use analytics and AI tools to understand your performance.",
          ],
          icon: Sparkles,
        },
        {
          eyebrow: "Step 1",
          title: "Start with your Dashboard",
          description:
            "Your Dashboard gives you a quick view of your trading performance, recent activity and important insights.",
          details: [
            "Review your trading overview.",
            "See recent performance and activity.",
            "Use shortcuts to move around TradePilot AI.",
          ],
          path: "/dashboard",
          action: "Open Dashboard",
          icon: LayoutDashboard,
        },
        {
          eyebrow: "Step 2",
          title: "Build your Trade Journal",
          description:
            "Record and review your trades so TradePilot AI can help you understand what is working and where you can improve.",
          details: [
            "Add or import your trades.",
            "Record notes and trading emotions.",
            "Review wins, losses and recurring behaviour.",
          ],
          path: "/trades",
          action: "Open Trade Journal",
          icon: WalletCards,
        },
        {
          eyebrow: "Step 3",
          title: "Create your Strategy Brain",
          description:
            "Strategy Brain defines how you trade. Add your markets, timeframes, entry rules, exits and risk limits.",
          details: [
            "Define the rules behind your trading decisions.",
            "Keep risk and trade-management rules structured.",
            "TradePilot AI can use the strategy when evaluating supported setups.",
          ],
          path: "/strategy-lab",
          action: hasPremium
            ? "Open Strategy Brain"
            : "View Premium",
          premium: true,
          icon: BrainCircuit,
        },
        {
          eyebrow: "Step 4",
          title: "Understand your performance",
          description:
            "Analytics, Trader DNA and AI tools help turn your journal into useful trading insights.",
          details: [
            "Find patterns across your trading history.",
            "Review strengths, weaknesses and consistency.",
            "Use AI features as analytical support, not guaranteed trading outcomes.",
          ],
          path:
            normalizedPlan === "free" && !isAdmin
              ? "/billing"
              : "/analytics",
          action:
            normalizedPlan === "free" && !isAdmin
              ? "View Plans"
              : "Open Analytics",
          icon: BarChart3,
        },
        {
          eyebrow: "Step 5",
          title: "Connect MT5 when you're ready",
          description: hasPremium
            ? "Premium traders can connect MT5, sync trading history, link Strategy Brain and review supported AutoTrader proposals."
            : "MT5 Trading is a Premium feature for account syncing, Strategy Brain linking and supported AutoTrader workflows.",
          details: [
            "Connect and sync supported MT5 trading history.",
            "Link an active Strategy Brain strategy.",
            "AutoTrader trade proposals require trader approval before supported live execution.",
          ],
          path: hasPremium
            ? "/mt5-trading"
            : "/billing",
          action: hasPremium
            ? "Open MT5 Trading"
            : "View Premium",
          premium: true,
          icon: Cable,
        },
        {
          eyebrow: "You're ready",
          title: "Start using TradePilot AI",
          description:
            "You can replay this tutorial whenever you need it. Start with your journal, build your strategy and use the data to improve your process.",
          details: [
            "Journal consistently.",
            "Follow a defined strategy.",
            "Review your performance and improve over time.",
          ],
          path: "/dashboard",
          action: "Go to Dashboard",
          icon: CheckCircle2,
        },
      ],
      [
        hasPremium,
        isAdmin,
        normalizedPlan,
      ],
    )

  useEffect(() => {
    const replay = () => {
      setStepIndex(0)
      setIsOpen(true)
    }

    window.addEventListener(
      ONBOARDING_REPLAY_EVENT,
      replay,
    )

    if (
      userId !== null &&
      userId !== undefined
    ) {
      const key = storageKey(userId)

      if (
        window.localStorage.getItem(key)
        !== "true"
      ) {
        setStepIndex(0)
        setIsOpen(true)
      } else {
        setIsOpen(false)
      }
    }

    return () => {
      window.removeEventListener(
        ONBOARDING_REPLAY_EVENT,
        replay,
      )
    }
  }, [userId])

  useEffect(() => {
    if (!isOpen) {
      return
    }

    const previous =
      document.body.style.overflow

    document.body.style.overflow =
      "hidden"

    return () => {
      document.body.style.overflow =
        previous
    }
  }, [isOpen])

  function completeTour() {
    window.localStorage.setItem(
      storageKey(userId),
      "true",
    )

    setIsOpen(false)
    setStepIndex(0)
  }

  function skipTour() {
    completeTour()
  }

  function finishAndNavigate() {
    const step = steps[stepIndex]

    completeTour()

    if (step.path) {
      navigate(step.path)
    }
  }

  if (!isOpen) {
    return null
  }

  const step =
    steps[stepIndex]

  const Icon =
    step.icon

  const isFirst =
    stepIndex === 0

  const isLast =
    stepIndex ===
    steps.length - 1

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 p-4 backdrop-blur-md sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-label="TradePilot AI tutorial"
    >
      <div className="relative w-full max-w-2xl overflow-hidden rounded-[2rem] border border-white/10 bg-[#0a101d] shadow-2xl">
        <div className="absolute inset-x-0 top-0 h-1 bg-white/[0.05]">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300"
            style={{
              width:
                `${((stepIndex + 1) / steps.length) * 100}%`,
            }}
          />
        </div>

        <div className="p-6 sm:p-8">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="grid size-14 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-blue-500/20 to-indigo-500/20 text-blue-300 ring-1 ring-blue-400/20">
                <Icon className="size-7" />
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">
                  {step.eyebrow}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  {stepIndex + 1}
                  {" "}
                  of
                  {" "}
                  {steps.length}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={skipTour}
              aria-label="Skip tutorial"
              className="grid size-10 shrink-0 place-items-center rounded-xl text-slate-500 transition hover:bg-white/[0.05] hover:text-white"
            >
              <X className="size-5" />
            </button>
          </div>

          <div className="mt-7">
            <div className="flex flex-wrap items-center gap-3">
              <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                {step.title}
              </h2>

              {step.premium ? (
                <span className="rounded-full border border-indigo-400/20 bg-indigo-500/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-indigo-300">
                  {hasPremium
                    ? "Premium enabled"
                    : "Premium"}
                </span>
              ) : null}
            </div>

            <p className="mt-4 max-w-xl text-sm leading-7 text-slate-400 sm:text-base">
              {step.description}
            </p>

            <div className="mt-6 space-y-3">
              {step.details.map(
                (detail) => (
                  <div
                    key={detail}
                    className="flex gap-3 rounded-2xl border border-white/[0.06] bg-white/[0.025] p-4"
                  >
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-400" />

                    <p className="text-sm leading-6 text-slate-300">
                      {detail}
                    </p>
                  </div>
                ),
              )}
            </div>
          </div>

          <div className="mt-8 flex flex-col-reverse gap-3 border-t border-white/10 pt-5 sm:flex-row sm:items-center sm:justify-between">
            <button
              type="button"
              onClick={skipTour}
              className="rounded-xl px-4 py-3 text-sm font-medium text-slate-400 transition hover:bg-white/[0.04] hover:text-white"
            >
              Skip tutorial
            </button>

            <div className="flex gap-3">
              {!isFirst ? (
                <button
                  type="button"
                  onClick={() =>
                    setStepIndex(
                      (current) =>
                        Math.max(
                          0,
                          current - 1,
                        ),
                    )
                  }
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/[0.05] sm:flex-none"
                >
                  <ChevronLeft className="size-4" />
                  Back
                </button>
              ) : null}

              {isLast ? (
                <button
                  type="button"
                  onClick={finishAndNavigate}
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 sm:flex-none"
                >
                  Start using TradePilot AI
                  <ChevronRight className="size-4" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() =>
                    setStepIndex(
                      (current) =>
                        Math.min(
                          steps.length - 1,
                          current + 1,
                        ),
                    )
                  }
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 sm:flex-none"
                >
                  {isFirst
                    ? "Start Tour"
                    : "Next"}

                  <ChevronRight className="size-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
