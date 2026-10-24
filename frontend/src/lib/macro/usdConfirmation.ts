import type { EventAnalysis, USDAnalysisResult } from "./usdEconomicEngine";

export type EvidenceCategory =
  | "inflation"
  | "labour"
  | "manufacturing"
  | "services"
  | "growth";

export type CategoryStance = "bullish" | "bearish" | "mixed";

export type ConfirmationLevel =
  | "strongly_confirmed"
  | "confirmed"
  | "partial"
  | "conflicted"
  | "insufficient";

export interface CategoryReading {
  category: EvidenceCategory;
  score: number;
  bullish: number;
  bearish: number;
  stance: CategoryStance;
}

export interface USDIntelligence {
  base: USDAnalysisResult;
  confirmation: ConfirmationLevel;
  baseConfidence: number;
  adjustedConfidence: number;
  categories: CategoryReading[];
  /** Events on the side of the bias. For a neutral bias: the bullish side. */
  supportingEvents: EventAnalysis[];
  /** Events against the bias. For a neutral bias: the bearish side. */
  opposingEvents: EventAnalysis[];
  conflictRatio: number;
  topDriverShare: number;
  explanation: string;
  risks: string[];
  invalidation: string[];
  unavailable: string[];
}

const CATEGORY_RULES: Array<[EvidenceCategory, string[]]> = [
  ["inflation", ["ppi", "cpi", "prices"]],
  ["services", ["services pmi"]],
  ["manufacturing", ["manufacturing", "factory orders", "industrial production"]],
  [
    "labour",
    [
      "employment",
      "nfp",
      "payroll",
      "jobless",
      "unemployment",
      "jolts",
      "job openings",
      "job cuts",
      "earnings",
      "adp",
    ],
  ],
];

const CONFIDENCE_FACTOR: Record<ConfirmationLevel, number> = {
  strongly_confirmed: 1,
  confirmed: 0.9,
  partial: 0.75,
  conflicted: 0.55,
  insufficient: 0.4,
};

const LEVEL_TEXT: Record<ConfirmationLevel, string> = {
  strongly_confirmed: "strongly confirmed across several categories",
  confirmed: "confirmed by multiple categories",
  partial: "not strongly confirmed because meaningful evidence points the other way",
  conflicted: "conflicted, with substantial evidence on both sides",
  insufficient: "based on too little directional evidence",
};

const BIAS_TEXT: Record<string, string> = {
  strong_bullish: "Strongly bullish",
  bullish: "Bullish",
  neutral: "Neutral",
  bearish: "Bearish",
  strong_bearish: "Strongly bearish",
};

const BIAS_THRESHOLD = 8;

function categoryOf(eventName: string): EvidenceCategory {
  const name = eventName
    .toLowerCase()
    .replace(/[^\w\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  for (const [category, keywords] of CATEGORY_RULES) {
    if (keywords.some((keyword) => name.includes(keyword))) {
      return category;
    }
  }

  return "growth";
}

function totalWeight(events: EventAnalysis[]): number {
  return events.reduce((total, event) => total + Math.abs(event.score), 0);
}

function largest(events: EventAnalysis[]): EventAnalysis | null {
  return events.length
    ? [...events].sort((a, b) => Math.abs(b.score) - Math.abs(a.score))[0]
    : null;
}

export function buildUSDIntelligence(
  result: USDAnalysisResult,
): USDIntelligence {
  const directional = result.events.filter((event) => event.score !== 0);
  const bullishEvents = directional.filter((event) => event.score > 0);
  const bearishEvents = directional.filter((event) => event.score < 0);
  const bullishWeight = totalWeight(bullishEvents);
  const bearishWeight = totalWeight(bearishEvents);

  const sign = result.bias.includes("bullish")
    ? 1
    : result.bias.includes("bearish")
      ? -1
      : 0;

  const supportingEvents = sign >= 0 ? bullishEvents : bearishEvents;
  const opposingEvents = sign >= 0 ? bearishEvents : bullishEvents;
  const supportWeight = sign >= 0 ? bullishWeight : bearishWeight;
  const opposeWeight = sign >= 0 ? bearishWeight : bullishWeight;
  const total = supportWeight + opposeWeight;

  const conflictRatio =
    total > 0
      ? sign === 0
        ? Math.min(bullishWeight, bearishWeight) / total
        : opposeWeight / total
      : 0;

  const topSupport = sign === 0 ? null : largest(supportingEvents);

  const topDriverShare =
    topSupport && supportWeight > 0
      ? Math.abs(topSupport.score) / supportWeight
      : 0;

  const grouped = new Map<
    EvidenceCategory,
    { score: number; bullish: number; bearish: number }
  >();

  for (const event of directional) {
    const category = categoryOf(event.event);
    const current = grouped.get(category) ?? {
      score: 0,
      bullish: 0,
      bearish: 0,
    };

    current.score += event.score;
    if (event.score > 0) current.bullish += 1;
    else current.bearish += 1;

    grouped.set(category, current);
  }

  const categories: CategoryReading[] = [...grouped.entries()]
    .map(([category, value]) => {
      const score = Number(value.score.toFixed(2));
      const stance: CategoryStance =
        Math.abs(score) < 2 ? "mixed" : score > 0 ? "bullish" : "bearish";

      return {
        category,
        score,
        bullish: value.bullish,
        bearish: value.bearish,
        stance,
      };
    })
    .sort((a, b) => Math.abs(b.score) - Math.abs(a.score));

  const bullishCategories = categories.filter((c) => c.stance === "bullish");
  const bearishCategories = categories.filter((c) => c.stance === "bearish");

  const agreeing =
    sign > 0 ? bullishCategories : sign < 0 ? bearishCategories : [];
  const opposingCategories =
    sign > 0 ? bearishCategories : sign < 0 ? bullishCategories : [];

  let confirmation: ConfirmationLevel;

  if (directional.length < 3) {
    confirmation = "insufficient";
  } else if (sign === 0) {
    confirmation = conflictRatio >= 0.3 ? "conflicted" : "insufficient";
  } else if (conflictRatio >= 0.4) {
    confirmation = "conflicted";
  } else if (
    conflictRatio < 0.2 &&
    agreeing.length >= 3 &&
    opposingCategories.length === 0
  ) {
    confirmation = "strongly_confirmed";
  } else if (
    conflictRatio < 0.25 &&
    agreeing.length >= 2 &&
    topDriverShare < 0.6
  ) {
    confirmation = "confirmed";
  } else {
    confirmation = "partial";
  }

  const concentrationPenalty = topDriverShare >= 0.6 ? 0.9 : 1;

  const adjustedConfidence = Math.round(
    result.confidence * CONFIDENCE_FACTOR[confirmation] * concentrationPenalty,
  );

  const names = (items: CategoryReading[]) =>
    items.map((item) => item.category).join(", ");

  const parts: string[] = [];

  if (sign === 0) {
    parts.push(
      `Neutral USD bias: the evidence is ${LEVEL_TEXT[confirmation]} (net score ${result.score}).`,
    );
    if (bullishCategories.length) {
      parts.push(`Bullish categories: ${names(bullishCategories)}.`);
    }
    if (bearishCategories.length) {
      parts.push(`Bearish categories: ${names(bearishCategories)}.`);
    }
    parts.push(
      `${bullishEvents.length} bullish vs ${bearishEvents.length} bearish scored events.`,
    );
  } else {
    parts.push(
      `${BIAS_TEXT[result.bias] ?? result.bias} USD bias, ${LEVEL_TEXT[confirmation]}.`,
    );
    if (agreeing.length) {
      parts.push(`Supporting categories: ${names(agreeing)}.`);
    }
    if (opposingCategories.length) {
      parts.push(`Opposing categories: ${names(opposingCategories)}.`);
    }
    parts.push(
      `${supportingEvents.length} supporting vs ${opposingEvents.length} opposing scored events.`,
    );
  }

  const risks: string[] = [];

  if (sign === 0) {
    const topBull = largest(bullishEvents);
    const topBear = largest(bearishEvents);

    if (topBull && topBear) {
      risks.push(
        `The bias could break either way. Largest bullish driver: ${topBull.event}; largest bearish driver: ${topBear.event}.`,
      );
    }
    risks.push(
      "Treat this as an unclear USD picture rather than a directional view.",
    );
  } else {
    if (opposingCategories.length) {
      risks.push(
        `Opposing evidence in ${names(opposingCategories)} weakens confirmation of this bias.`,
      );
    }

    if (conflictRatio >= 0.25) {
      risks.push(
        `About ${Math.round(conflictRatio * 100)}% of the scored evidence points against the bias.`,
      );
    }

    if (topSupport && topDriverShare >= 0.6) {
      risks.push(
        `Most of the support comes from one release (${topSupport.event}).`,
      );
    }
  }

  if (confirmation === "insufficient") {
    risks.push("Too few directional events to treat this as a reliable bias.");
  }

  const invalidation: string[] = [];

  if (sign === 0) {
    invalidation.push(
      `The bias turns bullish if the net score rises by about ${(BIAS_THRESHOLD - result.score).toFixed(1)} points, or bearish if it falls by about ${(result.score + BIAS_THRESHOLD).toFixed(1)} points.`,
    );
  } else {
    const margin = Math.abs(result.score) - BIAS_THRESHOLD;

    if (margin > 0) {
      invalidation.push(
        `The bias drops to neutral if the net score moves against it by about ${margin.toFixed(1)} points.`,
      );
    }

    invalidation.push(
      "A high-impact release (such as NFP, CPI or FOMC) surprising against the bias would weigh heavily.",
    );
  }

  const unavailable = [
    "Technical trend: not available from supplied evidence.",
    "Momentum and volatility: not available from supplied evidence.",
    "Key price levels: not available from supplied evidence.",
  ];

  const missingForecast = result.totalEvents - result.analysedEvents;

  if (missingForecast > 0) {
    unavailable.push(
      `${missingForecast} event(s) lacked forecast data and were not scored.`,
    );
  }

  return {
    base: result,
    confirmation,
    baseConfidence: result.confidence,
    adjustedConfidence,
    categories,
    supportingEvents,
    opposingEvents,
    conflictRatio: Number(conflictRatio.toFixed(3)),
    topDriverShare: Number(topDriverShare.toFixed(3)),
    explanation: parts.join(" "),
    risks,
    invalidation,
    unavailable,
  };
}
