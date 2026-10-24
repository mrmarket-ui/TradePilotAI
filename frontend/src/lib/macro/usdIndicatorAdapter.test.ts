import { analyseUSDEconomicEvents } from "./usdEconomicEngine";
import { buildUSDIntelligence } from "./usdConfirmation";
import { parseIndicatorValue, toUSDEvents } from "./usdIndicatorAdapter";

function close(a: number | null, b: number | null): boolean {
  if (a === null || b === null) return a === b;
  return Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b));
}

const parseCases: Array<[string | null, number | null]> = [
  ["55.4", 55.4],
  ["38K", 38000],
  ["-0.3%", -0.3],
  ["1,250K", 1250000],
  ["-$68.4B", -68.4e9],
  ["\u22120.2%", -0.2],
  ["1.2M", 1.2e6],
  ["0.3 m/m", 0.3],
  ["n/a", null],
  ["-", null],
  ["", null],
  [null, null],
];

console.log("--- PARSER ---");
let failures = 0;
for (const [input, expected] of parseCases) {
  const got = parseIndicatorValue(input);
  const ok = close(got, expected);
  if (!ok) failures += 1;
  console.log(`${ok ? "PASS" : "FAIL"}  ${JSON.stringify(input)} -> ${got} (expected ${expected})`);
}

console.log("\n--- ADAPTER ---");

const sample = {
  currency: "USD",
  extracted_indicators: [
    { indicator: "PPI m/m", actual: "1.6%", forecast: "1.2%", previous: "-0.3%" },
    { indicator: "ISM Services PMI", actual: "55.4", forecast: "54.2", previous: "53.8" },
    { indicator: "ADP Non-Farm Employment Change", actual: "38K", forecast: "47K", previous: "46K" },
    { indicator: "Unemployment Claims", actual: "206K", forecast: "205K", previous: "204K" },
    { indicator: "Trade Balance", actual: "-$68.4B", forecast: "-$70.1B", previous: "-$71.0B" },
    { indicator: "Fed Chair Speech", actual: null, forecast: null, previous: null },
    { indicator: "PPI m/m", actual: "1.6%", forecast: "1.2%", previous: "-0.3%" },
  ],
};

const result = toUSDEvents(sample);
console.log("Events:", result.events.length, "(expected 5: duplicate PPI and the speech are excluded)");
console.log("Skipped:", result.skipped);
if (result.events.length !== 5) failures += 1;

const nonUsd = toUSDEvents({ ...sample, currency: "EUR" });
console.log("Non-USD events:", nonUsd.events.length, "| reason:", nonUsd.reason);
if (nonUsd.events.length !== 0) failures += 1;

const intel = buildUSDIntelligence(analyseUSDEconomicEvents(result.events));
console.log("\nEnd to end:", intel.base.bias, "| score", intel.base.score, "|", intel.confirmation, "|", intel.baseConfidence, "->", intel.adjustedConfidence);
console.log(intel.explanation);

console.log(failures === 0 ? "\nALL CHECKS PASSED" : `\n${failures} CHECK(S) FAILED`);
