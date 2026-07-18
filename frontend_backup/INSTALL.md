# Install

Back up the old frontend, then replace its contents with this package.

```powershell
cd C:\Users\Theophollus\Development\TradePilotAI\frontend
Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item package-lock.json -Force -ErrorAction SilentlyContinue
Copy-Item .env.example .env -Force
npm install
npm run build
npm run dev
```

The package has no placeholder pages. Real affiliate URLs, PayPal credentials, broker execution, and unattended auto-trading remain intentionally unconfigured until launch credentials and risk controls exist.
