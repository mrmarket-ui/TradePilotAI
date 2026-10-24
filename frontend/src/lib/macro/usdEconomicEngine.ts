

export interface EconomicEvent {
  currency: string;
  event: string;
  actual: number | null;
  forecast: number | null;
  previous: number | null;
  impact?: "high" | "medium" | "low";
}

export type USDSignal =
  | "strong_bullish"
  | "bullish"
  | "neutral"
  | "bearish"
  | "strong_bearish";

export interface EventAnalysis {
  event: string;
  currency: string;
  actual: number | null;
  forecast: number | null;
  previous: number | null;
  impact: "high" | "medium" | "low";
  surprise: number | null;
  surprisePercent: number | null;
  direction: "bullish" | "bearish" | "neutral";
  score: number;
  reasoning: string;
}

export interface USDAnalysisResult {
  currency: "USD";
  bias: USDSignal;
  score: number;
  confidence: number;
  totalEvents: number;
  analysedEvents: number;
  bullishEvents: number;
  bearishEvents: number;
  neutralEvents: number;
  events: EventAnalysis[];
  summary: string;
  keyDrivers: EventAnalysis[];
}

const HIGHER_IS_BULLISH = [
  "nfp",
  "non-farm employment",
  "nonfarm employment",
  "adp non-farm employment",
  "adp nonfarm employment",
  "average hourly earnings",
  "retail sales",
  "core retail sales",
  "industrial production",
  "manufacturing pmi",
  "final manufacturing pmi",
  "services pmi",
  "final services pmi",
  "ism manufacturing pmi",
  "ism services pmi",
  "ism manufacturing prices",
  "ppi",
  "core ppi",
  "cpi",
  "core cpi",
  "gdp",
  "building permits",
  "housing starts",
  "consumer confidence",
  "consumer sentiment",
  "jolts job openings",
  "factory orders",
  "construction spending"
];

const LOWER_IS_BULLISH = [
  "unemployment rate",
  "unemployment claims",
  "initial jobless claims",
  "continuing jobless claims",
  "jobless claims",
  "challenger job cuts"
];

const HIGH_IMPACT = [
  "nfp",
  "non-farm employment",
  "nonfarm employment",
  "cpi",
  "core cpi",
  "fomc",
  "interest rate",
  "federal funds",
  "ism services",
  "ism manufacturing",
  "ppi"
];

const MEDIUM_IMPACT = [
  "adp",
  "jobless claims",
  "unemployment claims",
  "retail sales",
  "pmi",
  "jolts",
  "gdp",
  "factory orders",
  "construction spending",
  "trade balance"
];

const CONTEXT_ONLY = [
  "natural gas storage",
  "crude oil inventories",
  "api weekly statistical bulletin",
  "economic optimism",
  "vehicle sales"
];

function normalize(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^\w\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function contains(name: string, values: string[]): boolean {
  return values.some((value) => name.includes(normalize(value)));
}

/*
 * Month-on-month / quarter-on-quarter / year-on-year releases are small
 * numbers around zero, so a plain percentage of the forecast explodes
 * (for example -0.2 vs 0.1 reads as a -300% surprise). For these releases
 * the denominator has a floor so the surprise is scaled in percentage points.
 */
function isChangeIndicator(event: EconomicEvent): boolean {
  return /\b(m m|q q|y y|mom|qoq|yoy)\b/.test(normalize(event.event));
}
function impactFor(event: EconomicEvent): "high" | "medium" | "low" {
  if (event.impact) return event.impact;

  const name = normalize(event.event);

  if (name.startsWith("adp")) return "medium";
  if (contains(name, HIGH_IMPACT)) return "high";
  if (contains(name, MEDIUM_IMPACT)) return "medium";

  return "low";
}

function directionFor(
  event: EconomicEvent,
  surprise: number
): "bullish" | "bearish" | "neutral" {
  const name = normalize(event.event);

  if (contains(name, CONTEXT_ONLY)) {
    return "neutral";
  }

  /*
   * Trade Balance:
   * A less-negative balance means a smaller deficit and is generally
   * treated as a positive economic surprise.
   */
  if (name.includes("trade balance")) {
    return surprise > 0 ? "bullish" : surprise < 0 ? "bearish" : "neutral";
  }

  if (contains(name, LOWER_IS_BULLISH)) {
    return surprise < 0 ? "bullish" : surprise > 0 ? "bearish" : "neutral";
  }

  if (contains(name, HIGHER_IS_BULLISH)) {
    return surprise > 0 ? "bullish" : surprise < 0 ? "bearish" : "neutral";
  }

  return "neutral";
}

function magnitude(percent: number): number {
  const value = Math.abs(percent);

  if (value >= 30) return 1.5;
  if (value >= 15) return 1.3;
  if (value >= 7) return 1.15;
  if (value >= 2) return 1;
  return 0.7;
}

function scoreFor(
  event: EconomicEvent,
  direction: "bullish" | "bearish" | "neutral",
  surprisePercent: number
): number {
  if (direction === "neutral") return 0;

  const impact = impactFor(event);

  const base =
    impact === "high"
      ? 8
      : impact === "medium"
        ? 5
        : 2;

  const result = base * magnitude(surprisePercent);

  return Number(
    (direction === "bullish" ? result : -result).toFixed(2)
  );
}

function reasoningFor(
  event: EconomicEvent,
  direction: "bullish" | "bearish" | "neutral",
  surprisePercent: number
): string {
  if (event.actual === null || event.forecast === null) {
    return "Insufficient forecast data for directional analysis.";
  }

  const actual = event.actual;
  const forecast = event.forecast;
  const pct = Math.abs(surprisePercent).toFixed(1);

  if (direction === "bullish") {
    return `${actual} actual vs ${forecast} forecast — positive USD surprise of approximately ${pct}%.`;
  }

  if (direction === "bearish") {
    return `${actual} actual vs ${forecast} forecast — negative USD surprise of approximately ${pct}%.`;
  }

  return `${actual} actual vs ${forecast} forecast — neutral/contextual USD signal.`;
}

export function analyseUSDEvent(
  event: EconomicEvent
): EventAnalysis {
  const impact = impactFor(event);

  if (event.actual === null || event.forecast === null) {
    return {
      event: event.event,
      currency: event.currency,
      actual: event.actual,
      forecast: event.forecast,
      previous: event.previous,
      impact,
      surprise: null,
      surprisePercent: null,
      direction: "neutral",
      score: 0,
      reasoning: reasoningFor(event, "neutral", 0)
    };
  }

  const surprise = event.actual - event.forecast;

  const denominator =
    isChangeIndicator(event)
      ? Math.max(Math.abs(event.forecast), 2)
      : Math.abs(event.forecast) > 0.000001
        ? Math.abs(event.forecast)
        : 1;

  const surprisePercent =
    (surprise / denominator) * 100;

  const direction = directionFor(event, surprise);

  const score = scoreFor(
    event,
    direction,
    surprisePercent
  );

  return {
    event: event.event,
    currency: event.currency,
    actual: event.actual,
    forecast: event.forecast,
    previous: event.previous,
    impact,
    surprise,
    surprisePercent,
    direction,
    score,
    reasoning: reasoningFor(
      event,
      direction,
      surprisePercent
    )
  };
}

function biasFor(score: number): USDSignal {
  if (score >= 25) return "strong_bullish";
  if (score >= 8) return "bullish";
  if (score <= -25) return "strong_bearish";
  if (score <= -8) return "bearish";

  return "neutral";
}

function confidenceFor(
  events: EventAnalysis[],
  score: number
): number {
  const usable = events.filter(
    (event) => event.surprise !== null
  );

  if (!usable.length) return 0;

  const directional = usable.filter(
    (event) => event.direction !== "neutral"
  );

  const coverage =
    usable.length / events.length;

  const directionRatio =
    directional.length / usable.length;

  const scoreStrength =
    Math.min(Math.abs(score) / 40, 1);

  const confidence =
    (
      coverage * 35 +
      directionRatio * 25 +
      scoreStrength * 40
    );

  return Math.round(
    Math.min(95, Math.max(15, confidence))
  );
}

export function analyseUSDEconomicEvents(
  events: EconomicEvent[]
): USDAnalysisResult {
  const usdEvents = events.filter(
    (event) =>
      event.currency.toUpperCase() === "USD"
  );

  const analysed = usdEvents.map(
    analyseUSDEvent
  );

  const score = Number(
    analysed
      .reduce(
        (total, event) =>
          total + event.score,
        0
      )
      .toFixed(2)
  );

  const bullishEvents =
    analysed.filter(
      (event) =>
        event.direction === "bullish"
    ).length;

  const bearishEvents =
    analysed.filter(
      (event) =>
        event.direction === "bearish"
    ).length;

  const neutralEvents =
    analysed.filter(
      (event) =>
        event.direction === "neutral"
    ).length;

  const bias = biasFor(score);

  const confidence =
    confidenceFor(
      analysed,
      score
    );

  const keyDrivers =
    [...analysed]
      .filter(
        (event) =>
          event.score !== 0
      )
      .sort(
        (a, b) =>
          Math.abs(b.score) -
          Math.abs(a.score)
      )
      .slice(0, 5);

  let summary: string;

  if (!analysed.length) {
    summary =
      "No USD economic events were detected.";
  } else if (bias === "strong_bullish") {
    summary =
      `USD fundamental conditions are strongly bullish. The combined score is ${score}.`;
  } else if (bias === "bullish") {
    summary =
      `USD fundamental conditions are bullish. The combined score is ${score}.`;
  } else if (bias === "strong_bearish") {
    summary =
      `USD fundamental conditions are strongly bearish. The combined score is ${score}.`;
  } else if (bias === "bearish") {
    summary =
      `USD fundamental conditions are bearish. The combined score is ${score}.`;
  } else {
    summary =
      `USD economic evidence is mixed. The combined score is ${score}.`;
  }

  return {
    currency: "USD",
    bias,
    score,
    confidence,
    totalEvents: usdEvents.length,
    analysedEvents: analysed.filter(
      (event) =>
        event.surprise !== null
    ).length,
    bullishEvents,
    bearishEvents,
    neutralEvents,
    events: analysed,
    summary,
    keyDrivers
  };
}


