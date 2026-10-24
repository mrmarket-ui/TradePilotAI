import { toUSDEvents } from "./usdIndicatorAdapter";

const sample = {
  currency: "USD",
  extracted_indicators: [
    { indicator: "CAD Manufacturing PMI", actual: "51.5", forecast: "53.0", previous: "53.0" },
    { indicator: "Manufacturing PMI (CAD)", actual: "51.5", forecast: "53.0", previous: "53.0" },
    { indicator: "Final Manufacturing PMI", actual: "55.9", forecast: "56.9", previous: "57.0" },
    { indicator: "ISM Manufacturing PMI", actual: "54.5", forecast: "54.8", previous: "54.6" },
  ],
};

const result = toUSDEvents(sample);
const names = result.events.map((e) => e.event);
let failures = 0;

const check = (label: string, ok: boolean) => {
  if (!ok) failures += 1;
  console.log(`${ok ? "PASS" : "FAIL"}  ${label}`);
};

check("exactly 2 USD events kept", result.events.length === 2);
check("USD PMIs kept", names.includes("Final Manufacturing PMI") && names.includes("ISM Manufacturing PMI"));
check("both CAD rows skipped", result.skipped.length === 2);
console.log("Skipped:", result.skipped);

console.log(failures === 0 ? "\nALL CHECKS PASSED" : `\n${failures} CHECK(S) FAILED`);
