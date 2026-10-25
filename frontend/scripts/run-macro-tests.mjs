import { spawnSync } from "node:child_process"
import { readdirSync } from "node:fs"
import { join } from "node:path"

// Runs every macro test script and fails the build if any of them crashes
// or prints a failure marker (the scripts print but do not set exit codes).
const dir = join("src", "lib", "macro")
const files = readdirSync(dir)
  .filter((name) => name.endsWith(".test.ts"))
  .sort()

if (files.length === 0) {
  console.error("No macro test files found in " + dir)
  process.exit(1)
}

let failed = 0

for (const file of files) {
  const result = spawnSync(
    process.execPath,
    ["--import", "tsx", join(dir, file)],
    { encoding: "utf8" },
  )

  const output = (result.stdout ?? "") + (result.stderr ?? "")
  const bad =
    result.status !== 0 || /\bFAIL\b|CHECK\(S\) FAILED/.test(output)

  console.log((bad ? "FAIL  " : "PASS  ") + file)

  if (bad) {
    failed += 1
    console.log(output)
  }
}

console.log(
  failed === 0
    ? "\nAll " + files.length + " macro test files passed."
    : "\n" + failed + " of " + files.length + " macro test file(s) failed.",
)

process.exit(failed === 0 ? 0 : 1)