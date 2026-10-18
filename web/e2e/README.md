# Tests e2e (Playwright, Python)

Prerequis: `pip install playwright && playwright install chromium`, backend sur :8000 (base vierge),
`pnpm build && pnpm preview --port 4173`.

```bash
GTN_DB=/chemin/vers/backend/main.db python suite.py ../screenshots      # fonctionnel (38 verifications)
python matrix.py ../screenshots/final final                              # 9 ecrans x 8 viewports
python pwa.py ../screenshots                                             # manifest, service worker, hors ligne
```
