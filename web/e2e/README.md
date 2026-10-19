# Tests e2e (Playwright, Python)

Prerequis: `pip install playwright && playwright install chromium`, backend sur :8000 (base vierge, lance avec `uvicorn[standard]` pour les WebSocket),
`pnpm build && pnpm preview --port 4173`.

```bash
GTN_DB=/chemin/vers/backend/main.db python suite.py ../screenshots      # fonctionnel (38 verifications)
python matrix.py ../screenshots/final final                              # 9 ecrans x 8 viewports
python pwa.py ../screenshots                                             # manifest, service worker, hors ligne
GTN_DB=/chemin/vers/backend/main.db python powerups.py ../screenshots/powerups   # boutique -> inventaire -> bonus -> parties (18 verifications)

GTN_DB=/chemin/vers/backend/main.db python modes.py ../screenshots/modes        # Duel (2 navigateurs) + Mode Infini (30 verifications)

# API (30 tests, base temporaire, aucun serveur a lancer):
pip install pytest httpx && pytest backend/tests
```

## Scenes 3D

Sans GPU (SwiftShader, llvmpipe, Save-Data) l'accueil et le bonbon de jeu gardent le decor leger (SVG / cercle "???"),
ce qui garde Lighthouse a ~95. Les scripts ci-dessus testent donc ce chemin. Pour tester la 3D en headless:
`localStorage.setItem("force3d", "1")` (par ex. `context.add_init_script(...)`) et lancer Chromium avec
`--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`.
