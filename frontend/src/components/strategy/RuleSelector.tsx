type RuleSelectorProps = {
  title: string
  options: string[]
  selected: string[]
  onChange: (next: string[]) => void
}

export default function RuleSelector({
  title,
  options,
  selected,
  onChange,
}: RuleSelectorProps) {
  function toggle(option: string) {
    if (selected.includes(option)) {
      onChange(
        selected.filter(
          (item) => item !== option,
        ),
      )
      return
    }

    onChange([
      ...selected,
      option,
    ])
  }

  return (
    <section className="premium-card rounded-3xl p-6">
      <h3 className="text-lg font-semibold">
        {title}
      </h3>

      <div className="mt-4 flex flex-wrap gap-3">
        {options.map((option) => {
          const active =
            selected.includes(option)

          return (
            <button
              key={option}
              type="button"
              onClick={() => toggle(option)}
              className={[
                "rounded-2xl border px-4 py-2 text-sm transition",
                active
                  ? "border-blue-400/40 bg-blue-500/15 text-blue-200"
                  : "border-white/10 bg-white/[0.03] text-slate-400 hover:bg-white/[0.06]",
              ].join(" ")}
            >
              {option}
            </button>
          )
        })}
      </div>
    </section>
  )
}
