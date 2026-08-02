type ChipSelectorProps = {
  title: string
  description?: string
  options: string[]
  selected: string[]
  onChange: (next: string[]) => void
  allowCustom?: boolean
  customPlaceholder?: string
}

export default function ChipSelector({
  title,
  description,
  options,
  selected,
  onChange,
  allowCustom = false,
  customPlaceholder = "Add custom option",
}: ChipSelectorProps) {
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

  function addCustom(value: string) {
    const clean = value.trim()

    if (
      !clean ||
      selected.includes(clean)
    ) {
      return
    }

    onChange([
      ...selected,
      clean,
    ])
  }

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold">
          {title}
        </h2>

        {description ? (
          <p className="mt-2 text-sm leading-6 text-slate-400">
            {description}
          </p>
        ) : null}
      </div>

      <div className="flex flex-wrap gap-3">
        {options.map((option) => {
          const active =
            selected.includes(option)

          return (
            <button
              key={option}
              type="button"
              onClick={() => toggle(option)}
              className={[
                "rounded-2xl border px-4 py-2.5 text-sm font-medium transition",
                active
                  ? "border-blue-400/40 bg-blue-500/15 text-blue-200 shadow-lg shadow-blue-500/10"
                  : "border-white/10 bg-white/[0.03] text-slate-400 hover:border-blue-400/30 hover:bg-white/[0.06] hover:text-white",
              ].join(" ")}
            >
              {option}
            </button>
          )
        })}
      </div>

      {selected.length ? (
        <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Selected
          </p>

          <div className="mt-3 flex flex-wrap gap-2">
            {selected.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => toggle(item)}
                className="rounded-full border border-blue-400/20 bg-blue-400/[0.07] px-3 py-1.5 text-xs text-blue-300"
                title="Click to remove"
              >
                {item} ×
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {allowCustom ? (
        <form
          onSubmit={(event) => {
            event.preventDefault()

            const formData =
              new FormData(
                event.currentTarget,
              )

            const value = String(
              formData.get("custom") || "",
            )

            addCustom(value)
            event.currentTarget.reset()
          }}
          className="flex flex-col gap-3 sm:flex-row"
        >
          <input
            name="custom"
            placeholder={customPlaceholder}
            className="flex-1 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm outline-none transition focus:border-blue-400/40 focus:ring-4 focus:ring-blue-500/10"
          />

          <button
            type="submit"
            className="rounded-2xl border border-blue-400/20 bg-blue-400/[0.07] px-5 py-3 text-sm font-semibold text-blue-300 transition hover:bg-blue-400/10"
          >
            Add custom
          </button>
        </form>
      ) : null}
    </section>
  )
}
