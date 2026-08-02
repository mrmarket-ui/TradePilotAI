import type { StrategyForm } from "@/hooks/useStrategyBuilder"
import React from "react";

type Props = {
  data: {
    name: string;
    description: string;
    strategy_type: string;
  };
  update: (field: keyof StrategyForm, value: unknown) => void;
};

const strategyTypes = [
  "Scalping",
  "Day Trading",
  "Swing Trading",
  "Position Trading",
];

export default function GeneralStep({
  data,
  update,
}: Props) {
  return (
    <div className="space-y-6">

      <div>
        <h2 className="text-3xl font-bold">
          Strategy Information
        </h2>

        <p className="text-slate-400 mt-2">
          Give your strategy a professional identity.
        </p>
      </div>

      <div>
        <label className="block mb-2 font-medium">
          Strategy Name
        </label>

        <input
          className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3"
          value={data.name}
          onChange={(e) =>
            update("name", e.target.value)
          }
          placeholder="ICT London Liquidity Sweep"
        />
      </div>

      <div>
        <label className="block mb-2 font-medium">
          Description
        </label>

        <textarea
          rows={5}
          className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3"
          value={data.description}
          onChange={(e) =>
            update("description", e.target.value)
          }
          placeholder="Describe how this strategy works..."
        />
      </div>

      <div>
        <label className="block mb-3 font-medium">
          Strategy Type
        </label>

        <div className="grid grid-cols-2 gap-3">

          {strategyTypes.map((type) => (

            <button
              key={type}
              type="button"
              onClick={() =>
                update("strategy_type", type)
              }
              className={`rounded-xl border p-4 transition ${
                data.strategy_type === type
                  ? "border-blue-500 bg-blue-600 text-white"
                  : "border-slate-700 bg-slate-900 hover:border-blue-400"
              }`}
            >
              {type}
            </button>

          ))}

        </div>

      </div>

    </div>
  );
}
