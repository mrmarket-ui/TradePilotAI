import type { EconomicEvent } from "./usdEconomicEngine";

/** The subset of the General Macro response the adapter needs. */
export interface AdapterInput {
  currency?: string | null;
  extracted_indicators: Array<{
    indicator: string;
    actual?: string | null;
    forecast?: string | null;
    previous?: string | null;
  }>;
}

export interface AdapterResult {
  events: EconomicEvent[];
  skipped: string[];
  reason: string | null;
}

const MULTIPLIER: Record<string, number> = {
  k: 1e3,
  m: 1e6,
  b: 1e9,
  t: 1e12,
};

/**
 * Parses values such as "55.4", "38K", "-0.3%", "1,250K" or "-$68.4B".
 * Returns null for missing or non-numeric values.
 */
export function parseIndicatorValue(
  raw: string | null | undefined,
): number | null {
  if (raw === null || raw === undefined) return null;

  const text = String(raw)
    .trim()
    .replace(/\u2212/g, "-")
    .replace(/[$€£]/g, "")
    .replace(/,/g, "");

  if (!text) return null;

  const match = text.match(/(-?\d+(?:\.\d+)?)\s*([kmbt])?(?![A-Za-z0-9/])/i);
  if (!match) return null;

  const numberPart = match[1];
  if (numberPart === undefined) return null;

  const value = Number(numberPart);
  if (!Number.isFinite(value)) return null;

  const suffix = match[2];
  const multiplier = suffix ? (MULTIPLIER[suffix.toLowerCase()] ?? 1) : 1;

  return value * multiplier;
}

export function toUSDEvents(input: AdapterInput): AdapterResult {
  const currency = (input.currency ?? "").trim().toUpperCase();

  if (currency !== "USD") {
    return {
      events: [],
      skipped: [],
      reason: "Currency was not identified as USD, so the rules cross-check was not run.",
    };
  }

  const events: EconomicEvent[] = [];
  const skipped: string[] = [];
  const seen = new Set<string>();

  for (const item of input.extracted_indicators) {
    const actual = parseIndicatorValue(item.actual);
    const forecast = parseIndicatorValue(item.forecast);
    const previous = parseIndicatorValue(item.previous);

    if (actual === null) {
      skipped.push(`${item.indicator}: no numeric actual value`);
      continue;
    }

    const key = `${item.indicator.trim().toLowerCase()}|${actual}|${forecast}`;
    if (seen.has(key)) continue;
    seen.add(key);

    events.push({
      currency: "USD",
      event: item.indicator,
      actual,
      forecast,
      previous,
    });
  }

  return {
    events,
    skipped,
    reason: events.length ? null : "No indicators with numeric values were found.",
  };
}
