import {
  analyseUSDEconomicEvents,
  EconomicEvent,
} from "./usdEconomicEngine";

const testEvents: EconomicEvent[] = [
  {
    currency: "USD",
    event: "Final Manufacturing PMI",
    actual: 53.9,
    forecast: 53.3,
    previous: 53.2,
    impact: "medium",
  },

  {
    currency: "USD",
    event: "ISM Manufacturing PMI",
    actual: 54.6,
    forecast: 55.2,
    previous: 55.6,
    impact: "high",
  },

  {
    currency: "USD",
    event: "ISM Manufacturing Prices",
    actual: 71.1,
    forecast: 70.5,
    previous: 71.1,
    impact: "medium",
  },

  {
    currency: "USD",
    event: "JOLTS Job Openings",
    actual: 7.27,
    forecast: 7.33,
    previous: 7.18,
    impact: "medium",
  },

  {
    currency: "USD",
    event: "Construction Spending m/m",
    actual: -0.5,
    forecast: 0,
    previous: 0,
    impact: "low",
  },

  {
    currency: "USD",
    event: "ADP Non-Farm Employment Change",
    actual: 38,
    forecast: 47,
    previous: 46,
    impact: "medium",
  },

  {
    currency: "USD",
    event: "Factory Orders m/m",
    actual: 0.9,
    forecast: 0.7,
    previous: -0.2,
    impact: "medium",
  },

  {
    currency: "USD",
    event: "Crude Oil Inventories",
    actual: -4.5,
    forecast: -0.4,
    previous: 0.1,
    impact: "low",
  },

  {
    currency: "USD",
    event: "PPI m/m",
    actual: 1.6,
    forecast: 1.2,
    previous: -0.3,
    impact: "high",
  },

  {
    currency: "USD",
    event: "Unemployment Claims",
    actual: 206,
    forecast: 205,
    previous: 204,
    impact: "medium",
  },

  {
    currency: "USD",
    event: "Trade Balance",
    actual: -88.6,
    forecast: -89.4,
    previous: -71.2,
    impact: "low",
  },

  {
    currency: "USD",
    event: "Final Services PMI",
    actual: 56.5,
    forecast: 56.8,
    previous: 56.8,
    impact: "medium",
  },

  {
    currency: "USD",
    event: "ISM Services PMI",
    actual: 55.4,
    forecast: 54.2,
    previous: 54.1,
    impact: "high",
  },

  {
    currency: "USD",
    event: "Natural Gas Storage",
    actual: 30,
    forecast: 30,
    previous: 15,
    impact: "low",
  },
];

const result =
  analyseUSDEconomicEvents(
    testEvents
  );

console.log(
  "===================================="
);

console.log(
  "TRADEPILOT AI - USD MACRO TEST"
);

console.log(
  "===================================="
);

console.log(
  "USD Bias:",
  result.bias
);

console.log(
  "USD Score:",
  result.score
);

console.log(
  "Confidence:",
  `${result.confidence}%`
);

console.log(
  "Total Events:",
  result.totalEvents
);

console.log(
  "Analysed Events:",
  result.analysedEvents
);

console.log(
  "Bullish Events:",
  result.bullishEvents
);

console.log(
  "Bearish Events:",
  result.bearishEvents
);

console.log(
  "Neutral Events:",
  result.neutralEvents
);

console.log(
  "\nSUMMARY:"
);

console.log(
  result.summary
);

console.log(
  "\nKEY DRIVERS:"
);

result.keyDrivers.forEach(
  (event) => {
    console.log(
      `${event.event} | ${event.direction} | Score: ${event.score}`
    );

    console.log(
      `   ${event.reasoning}`
    );
  }
);

console.log(
  "\nALL EVENTS:"
);

result.events.forEach(
  (event) => {
    console.log(
      `${event.event}: ${event.direction} (${event.score})`
    );
  }
);

console.log(
  "===================================="
);