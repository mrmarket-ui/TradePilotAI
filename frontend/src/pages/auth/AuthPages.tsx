import {
  useEffect,
  useRef,
  useState,
  type ClipboardEvent,
  type FormEvent,
  type KeyboardEvent,
  type ReactNode,
} from "react"
import {
  Link,
  Navigate,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom"
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  Lock,
  Mail,
  User as UserIcon,
} from "lucide-react"
import { useTranslation } from "react-i18next"

import { useAuth } from "@/Auth"
import {
  errorMessage,
  registerAccount,
  requestPasswordReset,
  resendLoginCode,
  resetPassword,
  startLogin,
  verifyLoginCode,
  type AuthChallenge,
  type StartResult,
} from "@/api/auth"

import "./auth-glass.css"

const CODE_LENGTH = 6
const DOTS = "\u2022".repeat(10)
const TICK = "\u2713 "
const MIN_PASSWORD = 10

type Mode = "login" | "register"

type Step =
  | "credentials"
  | "code"
  | "forgot"
  | "forgotSent"
  | "reset"
  | "resetDone"

function safeDestination(value: unknown): string {
  return typeof value === "string" &&
    value.startsWith("/") &&
    !value.startsWith("//")
    ? value
    : "/dashboard"
}

function clock(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const rest = seconds % 60

  return `${String(minutes).padStart(2, "0")}:${String(rest).padStart(2, "0")}`
}

function useCountdown() {
  const [left, setLeft] = useState(0)

  useEffect(() => {
    if (left <= 0) {
      return
    }

    const id = window.setTimeout(() => setLeft((value) => value - 1), 1000)

    return () => window.clearTimeout(id)
  }, [left])

  return [left, setLeft] as const
}

/* ------------------------------------------------------------------ */
/* Form pieces                                                         */
/* ------------------------------------------------------------------ */

function PasswordField({
  id,
  label,
  value,
  onChange,
  autoComplete,
  placeholder,
}: {
  id: string
  label: string
  value: string
  onChange: (value: string) => void
  autoComplete: string
  placeholder: string
}) {
  const [visible, setVisible] = useState(false)

  return (
    <>
      <label className="ag-label" htmlFor={id}>
        {label}
      </label>

      <div className="ag-field">
        <Lock aria-hidden="true" />

        <input
          id={id}
          className="ag-input"
          type={visible ? "text" : "password"}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          autoComplete={autoComplete}
          placeholder={placeholder}
          required
        />

        <button
          type="button"
          className="ag-eye"
          onClick={() => setVisible((current) => !current)}
          aria-label={visible ? "Hide password" : "Show password"}
          aria-pressed={visible}
        >
          {visible ? <EyeOff aria-hidden="true" /> : <Eye aria-hidden="true" />}
        </button>
      </div>
    </>
  )
}

function CodeInput({
  value,
  onChange,
  disabled,
}: {
  value: string
  onChange: (value: string) => void
  disabled?: boolean
}) {
  const boxes = useRef<Array<HTMLInputElement | null>>([])

  useEffect(() => {
    boxes.current[Math.min(value.length, CODE_LENGTH - 1)]?.focus()
  }, [value.length])

  function accept(raw: string) {
    onChange(raw.replace(/\D/g, "").slice(0, CODE_LENGTH))
  }

  function handleChange(index: number, raw: string) {
    const digits = raw.replace(/\D/g, "")

    if (digits) {
      accept(value.slice(0, index) + digits)
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Backspace") {
      event.preventDefault()
      onChange(value.slice(0, -1))
    }
  }

  function handlePaste(event: ClipboardEvent<HTMLInputElement>) {
    event.preventDefault()
    accept(event.clipboardData.getData("text"))
  }

  return (
    <div className="ag-code" role="group" aria-label="One-time code">
      {Array.from({ length: CODE_LENGTH }, (_, index) => (
        <input
          key={index}
          ref={(element) => {
            boxes.current[index] = element
          }}
          className={`ag-code-box${
            index === value.length ? " ag-code-box--active" : ""
          }`}
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={CODE_LENGTH}
          autoComplete={index === 0 ? "one-time-code" : "off"}
          aria-label={`Digit ${index + 1} of ${CODE_LENGTH}`}
          value={value[index] ?? ""}
          disabled={disabled}
          onChange={(event) => handleChange(index, event.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          onFocus={(event) => event.target.select()}
        />
      ))}
    </div>
  )
}

function Busy({ busy, children }: { busy: boolean; children: ReactNode }) {
  return busy ? (
    <>
      <Loader2 className="ag-spin" aria-hidden="true" />
      {children}
    </>
  ) : (
    <>{children}</>
  )
}

/* ------------------------------------------------------------------ */
/* The glass card                                                      */
/* ------------------------------------------------------------------ */

function BrandRow() {
  return (
    <div className="auth-brand-row lg:hidden" style={{ marginBottom: "1.5rem" }}>
      <div className="auth-brand-mark">TP</div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-[.28em] text-blue-300">
          TradePilot AI
        </p>

        <p className="mt-1 text-xs text-slate-500">
          Trading intelligence workspace
        </p>
      </div>
    </div>
  )
}

function AuthPanel({ mode }: { mode: Mode }) {
  const { t } = useTranslation()
  const { completeLogin, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [params] = useSearchParams()

  const destination = safeDestination(
    (location.state as { from?: string } | null)?.from,
  )

  const [resetToken] = useState(() =>
    mode === "login" ? (params.get("reset") ?? "") : "",
  )

  const [step, setStep] = useState<Step>(resetToken ? "reset" : "credentials")
  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirm, setConfirm] = useState("")
  const [terms, setTerms] = useState(false)
  const [challenge, setChallenge] = useState<AuthChallenge | null>(null)
  const [code, setCode] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const [notice, setNotice] = useState("")
  const [resendIn, setResendIn] = useCountdown()

  // The reset token is kept in memory and removed from the address bar, so
  // it does not stay in the browser history or get copied by accident.
  useEffect(() => {
    if (params.get("reset")) {
      navigate(location.pathname, { replace: true })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function go(next: Step) {
    setStep(next)
    setError("")
    setNotice("")
  }

  async function handleResult(result: StartResult) {
    if (result.kind === "token") {
      await completeLogin(result.token.access_token)
      navigate(destination, { replace: true })
      return
    }

    setChallenge(result.challenge)
    setCode("")
    setResendIn(result.challenge.resend_in ?? 60)
    setPassword("")
    setConfirm("")
    go("code")
  }

  function checkNewPassword(): string {
    if (password.length < MIN_PASSWORD) {
      return t(
        "auth.passwordShort",
        `Use at least ${MIN_PASSWORD} characters for your password.`,
      )
    }

    if (password !== confirm) {
      return t("auth.passwordMismatch", "The passwords do not match.")
    }

    return ""
  }

  async function submitCredentials(event: FormEvent) {
    event.preventDefault()

    if (busy) {
      return
    }

    setError("")

    const cleanEmail = email.trim().toLowerCase()

    if (mode === "register") {
      const problem = checkNewPassword()

      if (problem) {
        setError(problem)
        return
      }

      if (!terms) {
        setError(
          t(
            "auth.termsRequired",
            "Please accept the Terms & Privacy Policy to create your account.",
          ),
        )
        return
      }
    }

    setBusy(true)

    try {
      const result =
        mode === "login"
          ? await startLogin(cleanEmail, password)
          : await registerAccount({
              fullName,
              email: cleanEmail,
              password,
            })

      setEmail(cleanEmail)
      await handleResult(result)
    } catch (caught) {
      setError(
        errorMessage(
          caught,
          mode === "login"
            ? "Invalid email or password."
            : "We could not create your account. Please try again.",
        ),
      )
    } finally {
      setBusy(false)
    }
  }

  async function submitCode(event: FormEvent) {
    event.preventDefault()

    if (busy || !challenge || code.length !== CODE_LENGTH) {
      return
    }

    setBusy(true)
    setError("")

    try {
      const token = await verifyLoginCode(challenge.challenge_id, code)

      await completeLogin(token.access_token)
      navigate(destination, { replace: true })
    } catch (caught) {
      setCode("")
      setError(
        errorMessage(caught, "That code is not correct. Please try again."),
      )
    } finally {
      setBusy(false)
    }
  }

  async function resend() {
    if (!challenge || resendIn > 0 || busy) {
      return
    }

    setBusy(true)
    setError("")
    setNotice("")

    try {
      const result = await resendLoginCode(challenge.challenge_id)

      setResendIn(result.resend_in)
      setCode("")
      setNotice(t("auth.codeResent", "A new code is on its way."))
    } catch (caught) {
      setError(
        errorMessage(caught, "Could not send a new code. Please try again."),
      )
    } finally {
      setBusy(false)
    }
  }

  async function submitForgot(event: FormEvent) {
    event.preventDefault()

    if (busy) {
      return
    }

    setBusy(true)
    setError("")

    try {
      await requestPasswordReset(email)
      go("forgotSent")
    } catch (caught) {
      setError(
        errorMessage(caught, "Could not send the reset link. Please try again."),
      )
    } finally {
      setBusy(false)
    }
  }

  async function submitReset(event: FormEvent) {
    event.preventDefault()

    if (busy) {
      return
    }

    const problem = checkNewPassword()

    if (problem) {
      setError(problem)
      return
    }

    setBusy(true)
    setError("")

    try {
      await resetPassword(resetToken, password)
      setPassword("")
      setConfirm("")
      go("resetDone")
    } catch (caught) {
      setError(
        errorMessage(
          caught,
          "This reset link is no longer valid. Request a new one.",
        ),
      )
    } finally {
      setBusy(false)
    }
  }

  if (isAuthenticated && !resetToken) {
    return <Navigate to={destination} replace />
  }

  const alert = (
    <div aria-live="polite">
      {error && (
        <div className="ag-error" role="alert">
          {error}
        </div>
      )}

      {notice && <div className="ag-notice">{notice}</div>}
    </div>
  )

  const backToSignIn = (
    <p className="ag-center">
      <button
        type="button"
        className="ag-link"
        onClick={() => {
          setPassword("")
          setConfirm("")
          go("credentials")
        }}
      >
        <ArrowLeft
          aria-hidden="true"
          style={{ width: "0.8rem", height: "0.8rem", verticalAlign: "-0.1rem" }}
        />{" "}
        {t("auth.backToSignIn", "Back to sign in")}
      </button>
    </p>
  )

  let content: ReactNode

  if (step === "code" && challenge) {
    content = (
      <form onSubmit={submitCode} noValidate>
        <div className="ag-badge">
          <KeyRound aria-hidden="true" />
        </div>

        <h2 className="ag-heading ag-title-center">
          {t("auth.verifyTitle", "Verify")} <span>OTP</span>
        </h2>

        <p className="ag-sub ag-title-center">
          {t("auth.codeSentTo", {
            defaultValue:
              "Enter the 6-digit security code we emailed to {{email}}.",
            email: challenge.email_hint,
          })}
          {mode === "register" &&
            ` ${t("auth.welcomeSent", "Your welcome email follows once you verify.")}`}
        </p>

        <CodeInput value={code} onChange={setCode} disabled={busy} />

        <p className="ag-hint ag-title-center">
          {t("auth.codeExpires", "The code expires in 10 minutes.")}
        </p>

        <p className="ag-center">
          {t("auth.noCode", "Didn't receive the code?")}{" "}
          {resendIn > 0 ? (
            <strong>
              {t("auth.resendIn", "Resend in")} {clock(resendIn)}
            </strong>
          ) : (
            <button
              type="button"
              className="ag-link"
              onClick={resend}
              disabled={busy}
            >
              {t("auth.resend", "Resend code")}
            </button>
          )}
        </p>

        {alert}

        <button
          type="submit"
          className="ag-btn ag-btn--gold"
          disabled={busy || code.length !== CODE_LENGTH}
        >
          <Busy busy={busy}>{t("auth.verify", "Verify & Proceed")}</Busy>
          {!busy && <ArrowRight aria-hidden="true" />}
        </button>

        {backToSignIn}
      </form>
    )
  } else if (step === "forgot") {
    content = (
      <form onSubmit={submitForgot}>
        <h2 className="ag-heading">
          {t("auth.forgotTitle", "Reset")} <span>{t("auth.forgotAccent", "password")}</span>
        </h2>

        <p className="ag-sub">
          {t(
            "auth.forgotSub",
            "Enter your account email and we will send you a link to choose a new password.",
          )}
        </p>

        <label className="ag-label" htmlFor="ag-forgot-email">
          {t("auth.email", "Email address")}
        </label>

        <div className="ag-field">
          <Mail aria-hidden="true" />

          <input
            id="ag-forgot-email"
            className="ag-input"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>

        {alert}

        <button type="submit" className="ag-btn" disabled={busy}>
          <Busy busy={busy}>{t("auth.sendLink", "Send reset link")}</Busy>
        </button>

        {backToSignIn}
      </form>
    )
  } else if (step === "forgotSent") {
    content = (
      <div>
        <div className="ag-badge">
          <Mail aria-hidden="true" />
        </div>

        <h2 className="ag-heading ag-title-center">
          {t("auth.checkEmail", "Check your")} <span>{t("auth.checkEmailAccent", "email")}</span>
        </h2>

        <p className="ag-sub ag-title-center">
          {t("auth.forgotSent", {
            defaultValue:
              "If an account exists for {{email}}, a reset link is on its way. It expires in 30 minutes.",
            email,
          })}
        </p>

        {backToSignIn}
      </div>
    )
  } else if (step === "reset") {
    content = (
      <form onSubmit={submitReset}>
        <h2 className="ag-heading">
          {t("auth.resetTitle", "Choose a new")} <span>{t("auth.resetAccent", "password")}</span>
        </h2>

        <p className="ag-sub">
          {t(
            "auth.resetSub",
            "Use a password you do not use anywhere else.",
          )}
        </p>

        <PasswordField
          id="ag-new-password"
          label={t("auth.newPassword", "New password")}
          value={password}
          onChange={setPassword}
          autoComplete="new-password"
          placeholder={DOTS}
        />

        <PasswordField
          id="ag-confirm-password"
          label={t("auth.confirmPassword", "Confirm password")}
          value={confirm}
          onChange={setConfirm}
          autoComplete="new-password"
          placeholder={DOTS}
        />

        <p className={`ag-hint${password.length >= MIN_PASSWORD ? " ag-hint--ok" : ""}`}>
          {password.length >= MIN_PASSWORD ? TICK : ""}
          {t("auth.passwordRule", `At least ${MIN_PASSWORD} characters.`)}
        </p>

        {alert}

        <button type="submit" className="ag-btn" disabled={busy}>
          <Busy busy={busy}>{t("auth.updatePassword", "Update password")}</Busy>
        </button>
      </form>
    )
  } else if (step === "resetDone") {
    content = (
      <div>
        <div className="ag-badge">
          <Check aria-hidden="true" />
        </div>

        <h2 className="ag-heading ag-title-center">
          {t("auth.resetDone", "Password")} <span>{t("auth.resetDoneAccent", "updated")}</span>
        </h2>

        <p className="ag-sub ag-title-center">
          {t(
            "auth.resetDoneSub",
            "For your security you were signed out everywhere. Sign in with your new password.",
          )}
        </p>

        <button
          type="button"
          className="ag-btn"
          onClick={() => go("credentials")}
        >
          {t("auth.signIn", "Sign in")}
          <ArrowRight aria-hidden="true" />
        </button>
      </div>
    )
  } else if (mode === "login") {
    content = (
      <form onSubmit={submitCredentials}>
        <BrandRow />

        <h2 className="ag-heading">
          {t("auth.welcomeBack", "Welcome")} <span>{t("auth.welcomeAccent", "back")}</span>
        </h2>

        <p className="ag-sub">
          {t(
            "auth.signInSub",
            "Sign in to continue to your TradePilot AI workspace.",
          )}
        </p>

        <label className="ag-label" htmlFor="ag-email">
          {t("auth.email", "Email address")}
        </label>

        <div className="ag-field">
          <Mail aria-hidden="true" />

          <input
            id="ag-email"
            className="ag-input"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>

        <PasswordField
          id="ag-password"
          label={t("auth.password", "Password")}
          value={password}
          onChange={setPassword}
          autoComplete="current-password"
          placeholder={t("auth.passwordPlaceholder", "Enter your password")}
        />

        <div className="ag-between">
          <span />

          <button
            type="button"
            className="ag-link"
            onClick={() => go("forgot")}
          >
            {t("auth.forgot", "Forgot password?")}
          </button>
        </div>

        {alert}

        <button type="submit" className="ag-btn" disabled={busy}>
          <Busy busy={busy}>{t("auth.signIn", "Sign in")}</Busy>
          {!busy && <ArrowRight aria-hidden="true" />}
        </button>

        <p className="ag-center">
          {t("auth.newHere", "New to TradePilot AI?")}{" "}
          <Link className="ag-link" to="/register">
            {t("auth.createAccount", "Create account")}
          </Link>
        </p>
      </form>
    )
  } else {
    content = (
      <form onSubmit={submitCredentials}>
        <BrandRow />

        <h2 className="ag-heading">
          {t("auth.createTitle", "Create")} <span>{t("auth.createAccent", "Account")}</span>
        </h2>

        <p className="ag-sub">
          {t(
            "auth.createSub",
            "Join us today to access your secure workspace.",
          )}
        </p>

        <label className="ag-label" htmlFor="ag-name">
          {t("auth.fullName", "Full name")}
        </label>

        <div className="ag-field">
          <UserIcon aria-hidden="true" />

          <input
            id="ag-name"
            className="ag-input"
            type="text"
            autoComplete="name"
            placeholder={t("auth.namePlaceholder", "Your name")}
            value={fullName}
            maxLength={80}
            onChange={(event) => setFullName(event.target.value)}
          />
        </div>

        <label className="ag-label" htmlFor="ag-email">
          {t("auth.email", "Email address")}
        </label>

        <div className="ag-field">
          <Mail aria-hidden="true" />

          <input
            id="ag-email"
            className="ag-input"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>

        <div className="ag-row">
          <div>
            <PasswordField
              id="ag-password"
              label={t("auth.password", "Password")}
              value={password}
              onChange={setPassword}
              autoComplete="new-password"
              placeholder={DOTS}
            />
          </div>

          <div>
            <PasswordField
              id="ag-confirm"
              label={t("auth.confirmPassword", "Confirm password")}
              value={confirm}
              onChange={setConfirm}
              autoComplete="new-password"
              placeholder={DOTS}
            />
          </div>
        </div>

        <p className={`ag-hint${password.length >= MIN_PASSWORD ? " ag-hint--ok" : ""}`}>
          {password.length >= MIN_PASSWORD ? TICK : ""}
          {t("auth.passwordRule", `At least ${MIN_PASSWORD} characters.`)}
        </p>

        <label className="ag-check">
          <input
            type="checkbox"
            checked={terms}
            onChange={(event) => setTerms(event.target.checked)}
          />

          <span>
            {t(
              "auth.terms",
              "I agree to the Terms & Privacy Policy, and I understand TradePilot AI is an educational tool, not financial advice.",
            )}
          </span>
        </label>

        {alert}

        <button type="submit" className="ag-btn" disabled={busy}>
          <Busy busy={busy}>{t("auth.createAccount", "Create account")}</Busy>
          {!busy && <ArrowRight aria-hidden="true" />}
        </button>

        <p className="ag-center">
          {t("auth.haveAccount", "Already have an account?")}{" "}
          <Link className="ag-link" to="/login">
            {t("auth.signIn", "Sign in")}
          </Link>
        </p>
      </form>
    )
  }

  return (
    <>
      <div className="ag-card">{content}</div>

      <p className="ag-footnote">
        Analytical and educational tools only. Trading involves financial risk.
      </p>
    </>
  )
}

/* ------------------------------------------------------------------ */
/* Left-hand panels (unchanged content from the existing pages)        */
/* ------------------------------------------------------------------ */

function BrandBlock() {
  return (
    <div className="auth-brand-row">
      <div className="auth-brand-mark">TP</div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-[.32em] text-blue-300">
          TradePilot AI
        </p>

        <p className="mt-1 text-xs text-slate-500">
          Trading intelligence workspace
        </p>
      </div>
    </div>
  )
}

function FeatureCards({ items }: { items: Array<[string, string]> }) {
  return (
    <>
      {items.map(([title, description]) => (
        <div key={title} className="auth-feature-card">
          <div className="auth-check">
            <Check className="size-4" />
          </div>

          <div>
            <p className="text-sm font-semibold text-slate-200">{title}</p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              {description}
            </p>
          </div>
        </div>
      ))}
    </>
  )
}

function LoginShowcase() {
  return (
    <section className="auth-showcase hidden lg:block">
      <BrandBlock />

      <div className="mt-12">
        <div className="auth-pill">AI-powered trading intelligence</div>

        <h1 className="mt-6 max-w-3xl text-5xl font-semibold leading-[1.06] xl:text-6xl">
          Understand your trading.
          <span className="auth-gradient-text block">
            Improve your process.
          </span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">
          TradePilot AI turns your journal, performance and trading behaviour
          into structured intelligence designed to support better
          decision-making.
        </p>
      </div>

      <div className="mt-10 grid max-w-2xl gap-4 sm:grid-cols-2">
        <FeatureCards
          items={[
            ["Trading Journal", "Capture every setup, result and lesson."],
            ["Performance Analytics", "See the patterns behind your results."],
            ["AI Coach", "Review psychology, risk and consistency."],
            [
              "Strategy Intelligence",
              "Build rules around how you actually trade.",
            ],
          ]}
        />
      </div>

      <div className="auth-trust-strip mt-8 max-w-2xl">
        <div>
          <p className="text-xs uppercase tracking-[.2em] text-slate-500">
            Built for
          </p>

          <p className="mt-1 text-sm font-medium">
            Process &middot; Discipline &middot; Review
          </p>
        </div>

        <div className="h-8 w-px bg-white/[.08]" />

        <div>
          <p className="text-xs uppercase tracking-[.2em] text-slate-500">
            Access
          </p>

          <p className="mt-1 text-sm font-medium">Free &middot; Pro &middot; Premium</p>
        </div>
      </div>
    </section>
  )
}

function RegisterShowcase() {
  return (
    <section className="auth-showcase">
      <BrandBlock />

      <div className="mt-10 lg:mt-12">
        <div className="auth-pill auth-pill-success">
          Free workspace included
        </div>

        <h1 className="mt-6 max-w-3xl text-4xl font-semibold leading-[1.08] sm:text-5xl xl:text-6xl">
          Build your edge with
          <span className="auth-gradient-text block">
            structured intelligence.
          </span>
        </h1>

        <p className="mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg sm:leading-8">
          Create your trading workspace, journal your decisions and turn
          performance data into insights you can actually use.
        </p>
      </div>

      <div className="mt-9 grid gap-4 sm:grid-cols-2">
        <FeatureCards
          items={[
            [
              "Professional Journal",
              "Track trades, setups, notes and outcomes in one workspace.",
            ],
            [
              "Advanced Analytics",
              "Measure performance, risk, consistency and behaviour.",
            ],
            [
              "AI Trading Coach",
              "Get analytical feedback on your process and psychology.",
            ],
            [
              "Strategy Brain",
              "Build, review and improve structured trading strategies.",
            ],
          ]}
        />
      </div>

      <div className="auth-free-card mt-8">
        <div>
          <p className="text-xs uppercase tracking-[.22em] text-emerald-300">
            Start free
          </p>

          <p className="mt-2 text-lg font-semibold">
            Your workspace is ready before you upgrade.
          </p>

          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
            Create an account and begin with TradePilot AI Free. Upgrade only
            when you want additional Pro or Premium intelligence.
          </p>
        </div>

        <div className="auth-free-badge">
          R0
          <span>FREE</span>
        </div>
      </div>

      <p className="mt-6 max-w-2xl text-xs leading-6 text-slate-600">
        TradePilot AI provides analytical and educational tools and does not
        guarantee profitability, investment results or trading performance.
      </p>
    </section>
  )
}

function AuthLayout({ mode }: { mode: Mode }) {
  const gridClass =
    mode === "login"
      ? "auth-grid mx-auto grid w-full max-w-7xl items-center gap-10 px-4 py-8 sm:px-6 lg:min-h-screen lg:grid-cols-[1.08fr_.92fr] lg:px-10"
      : "auth-grid mx-auto grid w-full max-w-7xl gap-10 px-4 py-8 sm:px-6 lg:min-h-screen lg:grid-cols-[1.08fr_.92fr] lg:items-center lg:px-10"

  return (
    <div className="auth-shell">
      <div className="auth-orb auth-orb-one" />
      <div className="auth-orb auth-orb-two" />

      <div className={gridClass}>
        {mode === "login" ? <LoginShowcase /> : <RegisterShowcase />}

        <section className="mx-auto w-full max-w-md">
          <AuthPanel mode={mode} />
        </section>
      </div>
    </div>
  )
}

export function LoginPage() {
  return <AuthLayout mode="login" />
}

export function RegisterPage() {
  return <AuthLayout mode="register" />
}
