type Props = {
  strengths: string[]
}

export default function ScoreStrengths({
  strengths,
}: Props) {
  return (
    <div className="premium-card rounded-3xl p-6">
      <h3 className="text-lg font-semibold">
        Strengths
      </h3>

      <ul className="mt-4 space-y-2">
        {strengths.map((item) => (
          <li
            key={item}
            className="text-emerald-300"
          >
            ✓ {item}
          </li>
        ))}
      </ul>
    </div>
  )
}
