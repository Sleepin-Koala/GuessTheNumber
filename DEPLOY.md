# Mettre le jeu en ligne

Cette page explique, pas à pas, comment publier Plus-Minus pour que des testeurs puissent y jouer depuis leur téléphone ou leur ordinateur. (Rédigée en anglais pour suivre les commandes des services.)

## The setup

```
 players' browsers
      │                         ┌──────────────────────────────┐
      ├── https://<site>.pages.dev ──▶│ Cloudflare Pages  (free)      │  the web app (static files)
      │                         └──────────────────────────────┘
      │                         ┌──────────────────────────────┐
      └── https://<api>.fly.dev ─────▶│ Fly.io: 1 machine + 1 GB volume│  API + WebSockets + database file
                                └──────────────────────────────┘
```

- **Web app → Cloudflare Pages, free plan.** Static files, HTTPS and a global CDN included.
- **Backend → Fly.io.** The backend is a Python server with WebSockets and a SQLite database file, so it needs a machine that stays on and a disk that survives restarts. Cloudflare's free plan hosts static sites and small JavaScript functions; this server could not run there without a rewrite.
- **Cost (Fly.io, checked when this was written — confirm on [fly.io pricing](https://fly.io/docs/about/pricing/)):** the smallest machine is about **$2.19 per 30 days** running non-stop, plus **$0.15 per GB per month** for the volume, so roughly **$3 per month**. There is no free allowance: a **credit card is required** once the short trial (about 2 hours of machine time or 7 days) ends. Cloudflare Pages needs no card.
- Why not a free web host? On free tiers (Render, for example) the disk is wiped on every restart and sleeping services drop WebSocket connections. Here that would delete every player account.

## Before you start

1. The code must be on GitHub (`origin` is already set to `Sleepin-Koala/GuessTheNumber`). Commits made on your computer are **not** online until you run `git push`.
2. Create two accounts: [Fly.io](https://fly.io) and [Cloudflare](https://dash.cloudflare.com/sign-up).
3. Install the Fly command line tool: <https://fly.io/docs/flyctl/install/>, then `fly auth login`.

## Step 1 — Deploy the API on Fly.io

Run everything from the `backend` folder.

```bash
cd backend
```

1. Pick a unique app name and put it on the first line of `backend/fly.toml` (`app = "…"`). Your API address will be `https://<app>.fly.dev`.
2. Create the app and its volume (the database lives on the volume; keep the region the same as in `fly.toml`):

```bash
fly apps create <app>
fly volumes create gtn_data --size 1 --region cdg
```

3. Deploy **one** machine (do not scale to two: rate limits and live connections are kept in memory, and a volume belongs to a single machine):

```bash
fly deploy --ha=false
```

4. Check it:

```bash
curl https://<app>.fly.dev/health        # → "En Bonne Sante"
fly status
```

## Step 2 — Deploy the web app on Cloudflare Pages

1. Cloudflare dashboard → **Workers & Pages** → create a new **Pages** project from an existing Git repository (the button labels change from time to time) → choose the repository.
2. Build settings:

| Setting | Value |
|---|---|
| Production branch | `main` |
| Root directory | `web` |
| Build command | `pnpm install --frozen-lockfile && pnpm build` |
| Build output directory | `dist` |

3. **Environment variables** (Production):

| Name | Value |
|---|---|
| `VITE_API_URL` | `https://<app>.fly.dev` |
| `NODE_VERSION` | `22` |

   `VITE_API_URL` is written into the app **at build time** (and into its security policy). If you change it later, trigger a new deployment.
4. Save and deploy. You get `https://<project>.pages.dev`.

## Step 3 — Allow the site to talk to the API

The API only accepts requests and WebSockets from websites it is told about:

```bash
cd backend
fly secrets set GTN_ALLOWED_ORIGINS=https://<project>.pages.dev
```

(This restarts the machine. Preview deployments of Cloudflare Pages use other addresses and are intentionally **not** allowed.)

## Step 4 — Check that it all works

From the `web/e2e` folder (needs `pip install playwright && playwright install chromium`):

```bash
python smoke.py https://<project>.pages.dev
```

It creates two throw-away accounts and plays a whole duel between two browsers over the real internet, checking HTTPS, CORS, WebSockets, direct links, the security policy and the offline mode (13 checks). Then try it by hand on a phone: open the site, **install it** (browser menu → "Add to home screen" / "Install app"), play each mode, and start a duel with a friend.

## Sharing with testers

Send the `https://<project>.pages.dev` address. Things worth knowing:

- Each browser gets its own anonymous account. Settings → **Copier mon code de récupération** lets a tester keep their progress or move to another device.
- The server limits **new accounts to 10 per hour per internet address**. Several testers on the same Wi-Fi share one address; if they are blocked (message "Trop de requêtes"), raise it: `fly secrets set GTN_NEW_ACCOUNTS_PER_HOUR=50`.
- Players only give a random nickname (changeable); no email or personal data is collected.

## Everyday operations

| Task | Command |
|---|---|
| See live logs | `cd backend && fly logs` |
| Machine status | `fly status` |
| Publish a new web version | `git push` (Cloudflare redeploys by itself) |
| Publish a new API version | `cd backend && fly deploy --ha=false` (or GitHub → Actions → **Deploy API to Fly.io** → Run workflow, after adding the secret `FLY_API_TOKEN` from `fly tokens create deploy`) |
| Out of memory | `fly scale memory 512` |
| Back up the database | `fly ssh sftp get /data/main.db ./backup-main.db` |
| Roll back the web app | Cloudflare dashboard → the project → Deployments → pick an older one → **Rollback** |
| Roll back the API | `git checkout <older commit>` then `fly deploy --ha=false` |
| Remove everything | `fly apps destroy <app>` (also delete the volume) and delete the Pages project |

An API deployment restarts the machine for a few seconds. Open games reconnect on their own, and the 30-second reconnection grace in Duel means nobody loses a game because of it. Fly can also snapshot volumes (see `fly volumes snapshots list`, and Fly's documentation for how long they are kept — not verified here), so don't rely on them alone: the manual copy above is a good habit before risky changes.

## Troubleshooting

| What you see | Likely cause and fix |
|---|---|
| The site opens but there is no player / everything says "Reconnexion…" | `VITE_API_URL` is wrong or was set after the build (redeploy the site), or the API address is not in `GTN_ALLOWED_ORIGINS` (check with `fly secrets list`). |
| Browser console: "blocked by CORS" or a CSP error mentioning the API | Same two causes; the origin must match exactly (`https`, no trailing slash). |
| "En direct" never appears, but the game works | WebSockets are refused: check `fly logs` for a refused origin or a token error. |
| "Trop de requêtes" when creating an account | Too many accounts from one address, see *Sharing with testers*. |
| After redeploying, every player has a new account | The volume is not mounted: `fly volumes list` must show `gtn_data` attached, and `GTN_DB_PATH` must be `/data/main.db` (the default in `fly.toml`). |
| Page not found on a direct link such as `/duel` | The `_redirects` file was not deployed; the root directory must be `web` so `web/public/_redirects` is copied. |

## Limits of this setup (on purpose, for a test phase)

- **One server machine.** A brief outage during each API deployment; do not add machines without first moving rate limiting and connection tracking to a shared store (Redis) and the database to Postgres.
- **SQLite on a 1 GB volume** is plenty for hundreds of players; a custom domain is optional (Cloudflare → Pages → Custom domains).
- The test containers used to validate this guide ran the same image Fly builds. What could **not** be tested from here: the real Fly.io and Cloudflare accounts, real phones, and the production domain names — `smoke.py` covers those once you deploy.
