# Tests e2e (Playwright, Python)

Prerequis: `pip install playwright && playwright install chromium`, backend sur :8000 (base vierge, lance avec `uvicorn[standard]` pour les WebSocket),
`pnpm build && pnpm preview --port 4173`.

```bash
GTN_DB=/chemin/vers/backend/main.db python suite.py ../screenshots      # fonctionnel (38 verifications)
python matrix.py ../screenshots/final final                              # 9 ecrans x 8 viewports
python pwa.py ../screenshots                                             # manifest, service worker, hors ligne
GTN_DB=/chemin/vers/backend/main.db python powerups.py ../screenshots/powerups   # boutique -> inventaire -> bonus -> parties (18 verifications)

GTN_DB=/chemin/vers/backend/main.db python modes.py ../screenshots/modes        # Duel (2 navigateurs) + Mode Infini (30 verifications)

DUEL_DISCONNECT_GRACE=4 DUEL_TURN_TIMEOUT=12 DUEL_WAIT_TIMEOUT=8 DUEL_SWEEP_INTERVAL=0.5   # (au lancement d'uvicorn)
python abandon.py ../screenshots/abandon                                   # abandon, deconnexion, inactivite, salle oubliee (17 verifications)

GTN_DB=/chemin/vers/backend/main.db python security.py ../screenshots/security  # jetons, migration, recuperation, CSP, debit (21 verifications)
#   -> lancer le backend SANS GTN_RATE_LIMIT=off pour celui-la, avec GTN_RATE_LIMIT=off pour tous les autres

# API (77 tests, base temporaire, aucun serveur a lancer):
pip install -r backend/requirements-dev.txt && pytest backend/tests
```

## Scenes 3D

Sans GPU (SwiftShader, llvmpipe, Save-Data) l'accueil et le bonbon de jeu gardent le decor leger (SVG / cercle "???"),
ce qui garde Lighthouse a ~95. Les scripts ci-dessus testent donc ce chemin. Pour tester la 3D en headless:
`localStorage.setItem("force3d", "1")` (par ex. `context.add_init_script(...)`) et lancer Chromium avec
`--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`.


## Apres un deploiement

`python smoke.py https://<site>.pages.dev` : 15 verifications sur le site en ligne (HTTPS, CORS, WebSocket, lien direct, CSP, PWA, hors ligne, duel complet entre deux navigateurs). Voir DEPLOY.md.
