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

// The USD rows from the real calendar paste (values in the units shown on the page).
const calendar: EconomicEvent[] = [
  ev("Core PCE Price Index m/m", 0.2, 0.3, 0.1),
  ev("Final GDP q/q", 2.2, 1.5, 1.5),
  ev("Final GDP Price Index q/q", 6.1, 6.4, 6.4),
  ev("Goods Trade Balance", -132.6, -116.3, -118.9),
  ev("Personal Income m/m", 0.2, 0.5, 0.3),
  ev("Personal Spending m/m", 0.9, 0.8, 0.1),
  ev("Prelim Wholesale Inventories m/m", 0.7, 0.5, 1.3),
  ev("Unemployment Claims", 197, 201, 198),
  ev("Final Manufacturing PMI", 55.9, 56.9, 57.0),
  ev("ISM Manufacturing PMI", 54.5, 54.8, 54.6),
  ev("Construction Spending m/m", 0.9, 0.0, -0.1),
  ev("ISM Manufacturing Prices", 77.9, 72.9, 71.1),
  ev("Omdia Total Vehicle Sales", 16.0, 16.3, 16.8),
  ev("Natural Gas Storage", 64, 63, 53),
];

const result = analyseUSDEconomicEvents(calendar);

console.log("EVENT | direction | impact | score");
for (const e of result.events) {
  console.log(`${e.event} | ${e.direction} | ${e.impact} | ${e.score}`);
}

const expectations: Array<[string, string, string]> = [
  ["Core PCE Price Index m/m", "bearish", "high"],
  ["Personal Income m/m", "bearish", "medium"],
  ["Personal Spending m/m", "bullish", "medium"],
  ["Prelim Wholesale Inventories m/m", "bullish", "low"],
  ["Goods Trade Balance", "bearish", "medium"],
  ["Omdia Total Vehicle Sales", "neutral", "low"],
];

let failures = 0;
console.log("\n--- CHECKS ---");
for (const [name, direction, impact] of expectations) {
  const found = result.events.find((e) => e.event === name);
  const ok = !!found && found.direction === direction && found.impact === impact;
  if (!ok) failures += 1;
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}: expected ${direction}/${impact}, got ${found ? found.direction + "/" + found.impact : "missing"}`);
}

const scored = result.bullishEvents + result.bearishEvents;
console.log(`\nScored directionally: ${scored} of ${result.totalEvents}`);

const intel = buildUSDIntelligence(result);
console.log("\nBias:", result.bias, "| score", result.score);
console.log("Confirmation:", intel.confirmation, "|", intel.baseConfidence, "->", intel.adjustedConfidence);
console.log(intel.explanation);
console.log("Categories:", intel.categories.map((c) => `${c.category} ${c.stance} (${c.score})`).join("; "));

console.log(failures === 0 ? "\nALL CHECKS PASSED" : `\n${failures} CHECK(S) FAILED`);
