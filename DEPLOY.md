# Mettre le jeu en ligne — gratuitement

Pas à pas pour publier Plus-Minus afin que des testeurs jouent depuis leur téléphone ou leur ordinateur, **sans payer**. (Rédigé en anglais pour suivre les écrans des services.)

## The setup (all free plans)

```
 players' browsers
      │                       ┌────────────────────────────┐
      ├─ https://<site>.pages.dev ──▶│ Cloudflare Pages            │  the web app (static files)
      │                       └────────────────────────────┘
      │                       ┌────────────────────────────┐        ┌──────────────────────┐
      └─ https://<api>.onrender.com ▶│ Render (free web service)   │ ─────▶ │ Neon (free Postgres)  │  accounts, scores, rooms
                              │ API + WebSockets            │        └──────────────────────┘
                              └────────────────────────────┘
```

| Part | Service | Why it fits |
|---|---|---|
| Web app | [Cloudflare Pages](https://pages.cloudflare.com) | free static hosting, HTTPS, CDN |
| API + WebSockets | [Render](https://render.com) free web service | runs the Docker image; free plan has 750 instance-hours a month ([docs](https://render.com/docs/free)) |
| Database | [Neon](https://neon.com/pricing) free plan | permanent free tier, no card, 0.5 GB, pauses itself after 5 idle minutes |

Why a separate database? Render's free plan wipes the server's disk on every restart or sleep, so a database file stored there would delete every player account. Neon keeps the data.

### What "free" means here — read this before inviting people

- **The server falls asleep** after 15 minutes without traffic and takes **about a minute** to wake ([Render docs](https://render.com/docs/free)). The first visitor after a quiet period waits; the site shows *"Le serveur se réveille, cela peut prendre jusqu'à une minute…"*. Since February 2026, messages on an open WebSocket count as activity ([changelog](https://render.com/changelog/free-web-services-now-remain-active-while-receiving-websocket-messages)), and the game sends one every 20 s while someone is connected, so it stays awake during play.
- **Limits:** 750 free instance-hours a month (one always-on service uses about 744), and Neon's free database has 100 compute-hours a month and 0.5 GB. The game releases its database connection after every request so Neon can pause when nobody plays; light testing stays well inside the limits. If you exceed one, that service is suspended until the next month.
- **Not verified when this was written:** whether Render asks for a card when you sign up (if it does and you have none, stop and tell me), and the exact button labels in each dashboard (they change).
- Free Postgres on **Render** expires after 30 days, which is why the database is on **Neon** instead.

## Before you start

1. The code must be on GitHub (already pushed to `Sleepin-Koala/GuessTheNumber`; pushes after this need `git push`).
2. Accounts: Cloudflare (done), [Neon](https://neon.com), [Render](https://render.com). Signing in with GitHub is the simplest way for Render.

## Step 1 — Create the database (Neon)

1. In Neon create a **project** (any name). Pick a region in Europe (closest to Render's Frankfurt).
2. Open the project's **Connect** dialog and copy the **connection string**. It looks like  
   `postgresql://user:password@ep-something.eu-central-1.aws.neon.tech/neondb?sslmode=require`  
   Keep it private: it is a password. (Either the direct or the "pooled" string works.)

The game creates its tables by itself on first start; there is nothing to import.

## Step 2 — Deploy the API (Render)

Option A — Blueprint (reads `render.yaml`): Render dashboard → **New** → **Blueprint** → pick the GitHub repository → Render shows the `plus-minus-api` service and asks for two values:

| Variable | Value |
|---|---|
| `GTN_DATABASE_URL` | the Neon connection string from step 1 |
| `GTN_ALLOWED_ORIGINS` | put `https://placeholder.invalid` for now (you set the real one in step 4) |

Option B — manually: **New** → **Web Service** → the repository, then:

| Setting | Value |
|---|---|
| Language / runtime | Docker |
| Root directory | `backend` |
| Dockerfile path | `./Dockerfile` |
| Instance type | **Free** |
| Region | Frankfurt |
| Health check path | `/health` |
| Environment | `GTN_DATABASE_URL`, `GTN_ALLOWED_ORIGINS` (as above), `GTN_TRUST_PROXY=1`, `GTN_PROXY_HOPS=1` |

When the first deploy succeeds, note the service address, `https://<name>.onrender.com`, and test it: `curl https://<name>.onrender.com/health` → `"En Bonne Sante"` (the first call may take a minute).

### Check the client address setting (important)

The game limits abuse per internet address, so the server must read the *player's* address, not Render's. From your own computer:

```bash
curl https://<name>.onrender.com/whoami      # → {"ip":"..."}
curl https://ifconfig.me                      # → your real public address
```

They must match. If `/whoami` shows another address, there is more than one proxy in front of the server: set `GTN_PROXY_HOPS=2` in Render and test again. (If this is wrong, all players share one address and the "10 new accounts per hour" limit applies to everybody together.)

## Step 3 — Deploy the web app (Cloudflare Pages)

Dashboard → **Workers & Pages** → create a **Pages** project from an existing Git repository → the repository. Settings:

| Setting | Value |
|---|---|
| Production branch | `main` |
| Root directory | `web` |
| Build command | `pnpm install --frozen-lockfile && pnpm build` |
| Build output directory | `dist` |
| Environment variable `VITE_API_URL` | `https://<name>.onrender.com` |
| Environment variable `NODE_VERSION` | `22` |

`VITE_API_URL` is baked into the app **at build time** (and into its security policy): if you change it, redeploy the site. You get `https://<project>.pages.dev`.

## Step 4 — Allow the site to talk to the API

In Render → the service → **Environment**: set `GTN_ALLOWED_ORIGINS` to `https://<project>.pages.dev` (exactly: `https`, no trailing slash). Render restarts the service.

## Step 5 — Check that it works

From the `web/e2e` folder (needs `pip install playwright && playwright install chromium`):

```bash
python smoke.py https://<project>.pages.dev
```

15 checks over the real internet: account creation, CORS, WebSockets, direct links, the security policy, offline mode, the "server waking up" message and a complete duel between two browsers. Then try by hand on a phone: open the site, **install it** (browser menu → *Add to home screen* / *Install app*), and play each mode.

## Sharing with testers

Send the `https://<project>.pages.dev` address. Tell them:
- the very first load after a quiet period can take up to a minute;
- each browser has its own anonymous account; Settings → **Copier mon code de récupération** keeps progress or moves it to another device;
- no email or personal data is collected, only a random nickname.

The server allows **10 new accounts per hour per internet address**; testers on one Wi-Fi share an address. If they get "Trop de requêtes", set `GTN_NEW_ACCOUNTS_PER_HOUR=50` in Render.

## Everyday operations

| Task | How |
|---|---|
| Live logs | Render dashboard → the service → **Logs** |
| New web version | `git push` — Cloudflare redeploys by itself |
| New API version | `git push` — Render redeploys (`autoDeploy`), or **Manual Deploy** in its dashboard |
| Change a setting | Render → **Environment** (restarts the service) |
| Roll back | Render: **Events/Deploys** → redeploy an older one · Cloudflare: Deployments → **Rollback** |
| Back up the data | Neon keeps a short restore history on the free plan (6 hours); for a copy: `pg_dump "<connection string>" > backup.sql` (needs the PostgreSQL client tools) |
| Remove everything | delete the Render service, the Neon project and the Pages project |

A restart of the API takes the service down for a minute; open games reconnect on their own, and Duel's 30-second reconnection grace means nobody loses a game because of a short outage.

## Troubleshooting

| What you see | Likely cause and fix |
|---|---|
| Site opens, banner "Le serveur se réveille…" | Normal after a quiet period; wait up to a minute. |
| No player / everything says "Reconnexion…" | `VITE_API_URL` wrong or set after the build (redeploy the site), or the site address is missing from `GTN_ALLOWED_ORIGINS`. |
| Browser console shows CORS or CSP errors naming the API | Same two causes; the origin must match exactly. |
| "En direct" never appears | WebSockets refused: check Render **Logs** for a refused origin or token. |
| "Trop de requêtes" on first visit | Too many accounts from one address, or `GTN_PROXY_HOPS` is wrong (see `/whoami` above). |
| Render log: `Could not parse SQLAlchemy URL` or `GTN_DATABASE_URL ... n'est pas une adresse PostgreSQL` | The value of `GTN_DATABASE_URL` is not a clean address. It must be exactly the string starting with `postgresql://` (no quotes, no `DATABASE_URL=`, no spaces). Fix it in Render → Environment. |
| Errors mentioning the database after weeks of use | Neon's free compute-hours may be used up (resets monthly) — check the Neon dashboard. |
| Page not found on a direct link such as `/duel` | Root directory must be `web` so `web/public/_redirects` is deployed. |

## If you can pay a little later: Fly.io

`backend/fly.toml` and the Dockerfile also deploy to [Fly.io](https://fly.io) (about $3 a month, card required) with a SQLite file on a persistent volume — no sleeping, no separate database: `cd backend && fly apps create <app> && fly volumes create gtn_data --size 1 --region cdg && fly deploy --ha=false`, then set `GTN_ALLOWED_ORIGINS` with `fly secrets set`. It is the same image and the same smoke test.

## Limits of this setup (on purpose, for a test phase)

- **One server instance only.** Rate limits and live connections are kept in memory; do not scale to several instances without a shared store (Redis).
- A free server is slow to wake and small; fine for friends and testers, not for a public launch.
- **Tested here:** the exact image running against a real PostgreSQL 16 (88 API tests pass on SQLite and on Postgres), database restart and pause recovery, container replacement, and the website built for a different API address, all over Docker. **Not tested from here:** the real Render, Neon and Cloudflare accounts and domains, real phones, and Render's `render.yaml` syntax (if the Blueprint is rejected, use *Option B*).
