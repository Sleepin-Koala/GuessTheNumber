# PWA / Responsive report: Guess the Number (web)

**Verdict: ADAPTIVE AND INSTALLABLE** on Chromium (emulated phone, tablet, desktop). **iOS / real-device install: UNVERIFIED** (no physical iPhone/Android; emulation only).

Evidence: `screenshots/final/<screen>-<viewport>.png` (72 images), `screenshots/before-*.png` (defects before the fixes), `screenshots/pwa.json`, `screenshots/lighthouse-summary.json`, `screenshots/suite.json`. Scripts: `web/e2e/`.

## Route x viewport (production build, no horizontal overflow, no console errors, state reachable)

| Screen | 360x640 | 390x844 | 430x932 | 768x1024 | 1024x768 | 1280x800 | 1920x1080 | 844x390-landscape |
|---|---|---|---|---|---|---|---|---|
| `/` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `/discovery` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `/classic` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `/shop` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `/stats` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `/duel` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `/endless` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `classic-game` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `discovery-game` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `settings` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

Checked per cell: `scrollWidth <= innerWidth`, element-off-screen scan, console errors (including Content-Security-Policy violations, since the production build ships a CSP), touch-target sizes, input font size. Screenshots were also reviewed by eye and by an independent subagent.

## Lighthouse (final secured production build, localhost)

| | Perf | A11y | Best Practices | SEO | LCP | CLS | TBT |
|---|---|---|---|---|---|---|---|
| Mobile | 97 | 100 | 100 | 100 | 2.3 s | 0.004 | 90 ms |
| Desktop | 100 | 100 | 100 | 100 | 0.6 s | 0.001 | 0 ms |

Mobile performance was 97 on four consecutive runs. (An earlier measurement of 75-91 was sandbox noise plus two real costs, both fixed: the audio library loading at start-up, and the account check blocking the first paint.) This Lighthouse version has no separate PWA category; installability was verified by hand (below).

## PWA checks

- Manifest: name, short_name, id, start_url, scope, `display: standalone`, colors, icons 192/512 + maskable 512, shortcuts. No orientation lock.
- `<link rel=manifest>`, theme-color, apple-touch-icon, iOS meta tags, `viewport-fit=cover`, zoom not disabled.
- Service worker registers, controls the page; app shell + every built asset precached (injected at build by `swPrecache` in `vite.config.js`), navigation network-first with shell fallback, API never cached, old caches purged, update prompt in `NetworkStatus.jsx`.
- Offline: `/` and a deep route (`/shop`) reload from the service worker and show an offline banner; API-dependent screens show placeholders. `offline.html` fallback exists.
- HTTPS is required for real deployments (localhost exempt): **UNVERIFIED**, no deployment target here.

## Functional test of every feature (43 checks)

- PASS Home: player auto-created
- PASS Home: starting wallet 500 coins / 5 gems / level 1
- PASS Home: header shows player name
- PASS Home: carousel can open /discovery
- PASS Home: carousel can open /classic
- PASS Home: carousel can open /endless
- PASS Home: carousel can open /duel
- PASS Home: carousel can open Settings overlay (no navigation)
- PASS Home: carousel can reach /shop
- PASS Home: carousel can reach /stats
- PASS Home: Settings overlay opens
- PASS Settings: rename saved on server
- PASS Settings: overlay closes after save
- PASS Settings: new name shown in header
- PASS Discovery: setup screen
- PASS Discovery: game starts (input visible)
- PASS Discovery: wrong guess shows 'Trop petit/Trop Grand' hint
- PASS Discovery: guesses recorded on server
- PASS Classic: level grid shown, only level 1 unlocked
- PASS Classic: start overlay (GO)
- PASS Classic: game panel loaded
- PASS Classic: win overlay
- PASS Classic: reward paid + level 2 unlocked
- PASS Classic: game-over overlay after attempts exhausted
- PASS Classic: lose recorded server-side
- PASS Classic: locked level (3) does not open
- PASS Sound: turning 'Effets sonores' off silences the game (no audio fetched)
- PASS Sound: with sound on, the click sound loads from the production build (200)
- PASS Sound: it is served as audio, not as the app's HTML page
- PASS Shop: tab Bonus shows items
- PASS Shop: tab Indices shows items
- PASS Shop: tab Aide shows items
- PASS Shop: purchase debits coins
- PASS Shop: header coins updated
- PASS Shop: buy button not offered when too poor
- PASS Shop: Retour goes home
- PASS Stats: history lists discovery + classic games
- PASS Stats: shows Victoire and Défaite
- PASS Stats: Retour goes home
- PASS Duel (web): lobby is shown
- PASS API: negative endless bet rejected
- PASS API: fake classic win rejected
- PASS Console: no unexpected errors (deliberate 402/422/404 probes excluded)

Other suites: power-ups 18, Duel/Endless/real-time 38, abandonment 17, security 21 (browser); 77 API tests.

## Defects fixed (file)

- Header title overlapped player name / badges on narrow screens: `components/PlayerProps.jsx` (title hidden below md, truncation, compact badges, safe-area padding).
- Game panel clipped on short/small screens (guess button unreachable): `components/GameplayPanel.jsx`, `mode/Solo/Level.jsx`, `mode/Discovery/game.jsx` (scrollable, compact sizes, decorative circle hidden on short heights).
- Home carousel arrows covered card text; cards too narrow on phones: `components/Carrousel.jsx`, `Home.jsx`.
- Classic levels: single-column list on phones, pages reachable only with arrow keys, hidden rows in landscape: `mode/Solo/SelectionScreen.jsx` (4 columns, prev/next buttons, scroll, `aria-disabled`).
- Stats header clipped long names, cramped chart/table: `mode/stats/main.jsx`.
- Touch targets under 44px (dots, buy button, Retour, pause, settings close, shop tabs, level pager) and label contrast; carousel dots had no accessible name.
- `100vh`/`h-screen` replaced by `dvh`; `w-screen` by `w-full`; touch-action / overscroll in `index.css`.
- Header always showed "Niv. 1": the level prop was never passed (Home, Discovery, Classic).
- Empty `/duel` page; `GET /user/null` console error on first visit (`Home.jsx`).
- No manifest / service worker / icons / robots.txt / theme-color: added under `web/public`, `index.html`, `src/main.jsx`.
- Route code-splitting (mobile LCP 2.6 s to 2.1 s): `App.jsx`.

## Remaining issues / UNVERIFIED

- Real-device testing (iOS Safari install, Android install prompt, notch/safe-area bottom inset): UNVERIFIED. Safe-area is applied to the header and offline banner only.
- Settings sound toggle track is 48x24 px (meets WCAG 2.2 AA 24px, below the 44px guideline).
- Home carousel cards are tall with empty space on large phones; Shop cards are left-aligned on very wide screens (cosmetic).
- Stats win-rate donut renders very small; decorative joystick in Settings extends past the card edge on phones (no scroll).
- 200% zoom and keyboard-only navigation on desktop were not exhaustively tested; Duel gameplay, Endless mode and power-up effects do not exist in the web client.

## Design pass (3D orb, fonts, micro-animations)

Re-verified after the design pass: functional suite 38/38, viewport matrix 72/72, offline OK, Lighthouse mobile 95/100/100/100 (LCP 2.4 s), desktop 100/100/100/100. Orb screenshots: `screenshots/design/`. The orb was captured with software WebGL (SwiftShader) in headless Chromium; real-GPU frame rate on phones is UNVERIFIED. The Three.js chunk (~252 kB gzipped) loads only when a game starts and is not precached.

### 3D Home scene

`HomeBackdrop` keeps the SVG night backdrop and fades in a Three.js scene (30 glossy digit candies, fog, stars, pointer parallax) after idle. It is skipped without hardware WebGL, with Save-Data, and is static under `prefers-reduced-motion`. Without that guard, software WebGL dropped Lighthouse mobile performance to 56; with it: mobile 94/100/100/100 (LCP 2.4 s), desktop 100/100/100/100. The 3D chunk (~928 kB, ~254 kB gzip) is loaded on demand and excluded from the service-worker precache. Real-GPU frame rate: UNVERIFIED. Screenshots: `screenshots/design/home3d-*`.

## Later fixes found by re-checking the final build

- Sounds were broken in production (paths like `src/sounds/x.mp3` exist only on the dev server): audio files are now bundled; the "Effets sonores" setting is now honoured (it was never read); the audio library loads on first play instead of at start-up.
- The account check no longer blocks the first paint (`AccountGate` on game screens; Home renders immediately).
