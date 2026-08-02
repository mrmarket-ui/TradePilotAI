type Props = {
  weaknesses: string[]
}

export default function ScoreWeaknesses({
  weaknesses,
}: Props) {
  return (
    <div className="premium-card rounded-3xl p-6">
      <h3 className="text-lg font-semibold">
        Weaknesses
      </h3>

      <ul className="mt-4 space-y-2">
        {weaknesses.map((item) => (
          <li
            key={item}
            className="text-red-300"
          >
            • {item}
          </li>
        ))}
      </ul>
    </div>
  )
}
