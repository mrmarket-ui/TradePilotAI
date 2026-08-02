export const supportedCurrencies = [
  { code: "USD", name: "US Dollar" },
  { code: "ZAR", name: "South African Rand" },
  { code: "EUR", name: "Euro" },
  { code: "GBP", name: "British Pound" },
  { code: "CAD", name: "Canadian Dollar" },
  { code: "AUD", name: "Australian Dollar" },
  { code: "JPY", name: "Japanese Yen" },
  { code: "CNY", name: "Chinese Yuan" },
  { code: "INR", name: "Indian Rupee" },
  { code: "NGN", name: "Nigerian Naira" },
  { code: "AED", name: "UAE Dirham" },
] as const

const locales: Record<string, string> = {
  en: "en-US",
  af: "af-ZA",
  fr: "fr-FR",
  es: "es-ES",
}

export function localeForLanguage(
  language = "en",
) {
  return (
    locales[
      language.split("-")[0]
    ] || "en-US"
  )
}

export function formatMoney(
  amount: number,
  currency = "USD",
  language = "en",
) {
  return new Intl.NumberFormat(
    localeForLanguage(language),
    {
      style: "currency",
      currency,
    },
  ).format(amount)
}
