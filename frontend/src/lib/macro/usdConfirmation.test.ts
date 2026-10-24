import {
  analyseUSDEconomicEvents,
  type EconomicEvent,
} from "./usdEconomicEngine";
import { buildUSDIntelligence } from "./usdConfirmation";

const ev = (
  event: string,
  actual: number,
  forecast: number,
  previous: number,
): EconomicEvent => ({ currency: "USD", event, actual, forecast, previous });

// Illustrative fixtures only - not your real calendar data.
const scenarios: Record<string, EconomicEvent[]> = {
  "A: MIXED (inflation up, labour down)": [
    ev("PPI m/m", 1.6, 1.2, -0.3),
    ev("ISM Services PMI", 55.4, 54.2, 53.8),
    ev("Factory Orders m/m", 0.9, 0.7, 0.5),
    ev("ISM Manufacturing PMI", 54.6, 55.2, 55.6),
    ev("Final Manufacturing PMI", 53.9, 53.3, 53.3),
    ev("JOLTS Job Openings", 7.1, 7.3, 7.2),
    ev("Unemployment Claims", 206, 205, 204),
    ev("Final Services PMI", 54.0, 54.5, 54.1),
    ev("Construction Spending m/m", -0.2, 0.1, 0.0),
    ev("ADP Non-Farm Employment Change", 38, 47, 46),
  ],
  "B: BULLISH with labour opposing": [
    ev("PPI m/m", 1.6, 1.2, -0.3),
    ev("ISM Services PMI", 55.4, 54.2, 53.8),
    ev("Factory Orders m/m", 0.9, 0.7, 0.5),
    ev("ISM Manufacturing PMI", 54.6, 55.2, 55.6),
    ev("Final Manufacturing PMI", 53.9, 53.3, 53.3),
    ev("JOLTS Job Openings", 7.1, 7.3, 7.2),
    ev("Unemployment Claims", 206, 205, 204),
  ],
};

for (const [label, events] of Object.entries(scenarios)) {
  const intel = buildUSDIntelligence(analyseUSDEconomicEvents(events));

  console.log("\n====================================");
  console.log("SCENARIO " + label);
  console.log("====================================");
  console.log("Bias:", intel.base.bias, "| Score:", intel.base.score);
  console.log("Confirmation:", intel.confirmation);
  console.log("Confidence:", intel.baseConfidence, "->", intel.adjustedConfidence);
  console.log("Conflict ratio:", intel.conflictRatio, "| Top driver share:", intel.topDriverShare);
  console.log("\nEXPLANATION:\n" + intel.explanation);
  console.log("\nCATEGORIES:");
  intel.categories.forEach((c) =>
    console.log(` ${c.category}: ${c.stance} (${c.score})`),
  );
  console.log("\nRISKS:");
  intel.risks.forEach((r) => console.log(" -", r));
  console.log("\nINVALIDATION:");
  intel.invalidation.forEach((r) => console.log(" -", r));
}
