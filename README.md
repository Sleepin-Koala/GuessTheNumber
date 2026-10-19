# Plus-Minus — Guess the Number

Un jeu de devinette en ligne : trouve le nombre mystère en un minimum d'essais, seul ou contre un autre joueur, avec une boutique, des power-ups, des statistiques et un décor 3D. Application web installable (PWA), adaptée au téléphone, à la tablette et à l'ordinateur.

## Modes de jeu

| Mode | Principe |
|---|---|
| **Découverte** | Essais illimités, indices « Trop petit / Trop grand », plage au choix (jusqu'à 100 000). Aucune récompense. |
| **Classique** | Niveaux 1 à 1000 : nombre d'essais et temps limités. Récompenses en pièces, XP, étoiles (1 à 3) et gemmes (3 étoiles) ; gagner le niveau actuel débloque le suivant. |
| **Infini** | On mise des pièces, 5 essais par palier. Un palier gagné rapporte `mise × 1,25^palier` ; on encaisse ou on remise tout sur le palier suivant. Perdre fait perdre la mise du palier. |
| **Duel** | Deux joueurs : chacun cache un nombre puis cherche celui de l'autre, le moins d'essais gagne la mise (égalité : l'hôte). Temps réel par WebSocket, abandon, déconnexions et inactivité gérés. |

Autour des modes : **boutique** (8 power-ups) avec **inventaire** par joueur, **bonus avant la partie** (+3 essais, Indice, Rage), **statistiques**, paramètres (pseudo, son, code de récupération du compte).

### Power-ups

| Objet | Effet |
|---|---|
| Nombre Pair | dit si le nombre est pair ou impair |
| Premier / Parfait | dit si le nombre est premier / parfait |
| Scan | donne une plage de moitié de la plage totale qui contient le nombre |
| Conseiller IA | suggère le milieu de ce qui reste possible d'après tes essais |
| Vie bonus | +3 essais |
| Ralenti | double le temps restant (au moins +5 s), mode Classique |
| Multiplicateur x2 | double les pièces gagnées (Classique, avant le premier essai) |

Chaque objet s'utilise une fois par partie et est consommé de l'inventaire ; tout est appliqué côté serveur.

## Technologies

- **Web** : React 19, Vite 7, Tailwind CSS 4, React Router, Framer Motion, **Three.js** (`@react-three/fiber`) pour le bonbon mystère et le décor de l'accueil (chargés à la demande, remplacés par un décor léger sans GPU), Recharts, Howler (sons chargés au premier usage), polices Lilita One et Nunito auto-hébergées. PWA : manifeste, service worker maison (shell + fichiers du build en cache, page hors ligne, invite de mise à jour).
- **Serveur** : Python, FastAPI, SQLAlchemy 2, uvicorn[standard] (WebSocket). Base **SQLite** (`main.db`) par défaut, **PostgreSQL** (Neon, etc.) avec `GTN_DATABASE_URL`.

## Structure

```
backend/
  main.py            application, CORS, middleware, tâche de fond
  security.py        limitation de débit, en-têtes, origines autorisées
  database.py        modèles SQLAlchemy + migrations légères des colonnes ajoutées
  engine/            règles du jeu (niveaux, scores, récompenses, power-ups)
  routes/            user, shop, game (+ game_mode/: classic, discovery, endless, duel), powerups,
                     auth (jetons), realtime (diffusion WebSocket)
  assets/Powerup.json  catalogue de la boutique
  Dockerfile, fly.toml   image du serveur et variante Fly.io (voir DEPLOY.md)
render.yaml          Blueprint Render (offre gratuite)
  tests/             tests de l'API (pytest)
web/
  src/               pages (mode/), composants, hooks, API client
  public/            manifeste, service worker, icônes, _headers / _redirects (hébergement)
  e2e/               tests navigateur (Playwright, Python)
screenshots/         captures de vérification (responsive, modes, sécurité)
PWA_RESPONSIVE_REPORT.md   rapport de vérification responsive / PWA / Lighthouse
```

## Lancer en local

Prérequis : Python 3.11+, Node 20.19+ avec pnpm.

```bash
# 1. Serveur (http://127.0.0.1:8000)
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend && uvicorn main:app --port 8000
```

```bash
# 2. Web (http://localhost:5173)
cd web
pnpm install
pnpm dev
```

Pour un autre serveur d'API : `VITE_API_URL=https://api.exemple.com pnpm build` (l'adresse est aussi reprise dans la Content-Security-Policy du build). Le build de production : `pnpm build` puis `pnpm preview --port 4173`. Au premier lancement, la base `backend/main.db` est créée toute seule ; elle est ignorée par git.

## Tests

```bash
pip install -r backend/requirements-dev.txt
pytest backend/tests          # 89 tests de l'API (comptes, jeu, power-ups, duel, temps réel, abandon, sécurité)
GTN_TEST_DATABASE_URL=postgresql://user:mdp@hote/base pytest backend/tests   # les mêmes tests sur PostgreSQL (la base est vidée !)
```

Tests navigateur (Playwright) : voir `web/e2e/README.md` (dont `smoke.py`, un test de fumée à lancer sur le site en ligne) — parcours complet de chaque mode, deux joueurs dans deux navigateurs, sons, PWA hors ligne, matrice responsive de 10 écrans × 8 tailles, sécurité.

## API (résumé)

Toutes les routes exigent le jeton du joueur (sauf `/health`, `/user/new_player`, `/user/claim`).

| Domaine | Routes |
|---|---|
| Compte | `POST /user/new_player`, `POST /user/claim`, `GET /user/me`, `GET /user/{id}`, `POST /user/rename`, `GET /user/stats/{id}`, `GET /user/stats/history/{id}` |
| Parties | `POST /game/guess`, `POST /game/powerup` |
| Classique | `POST /game/classic/level`, `POST /game/classic/end_level` |
| Découverte | `POST /game/discovery/start`, `POST /game/discovery/end_session` |
| Infini | `POST /game/endless/start`, `POST /game/endless/end_session` |
| Boutique | `POST /shop/buy`, `POST /shop/count`, `GET /shop/inventory/{id}` |
| Duel | `GET /game/duel/rooms`, `POST /game/duel/{host,status,join}`, `POST /game/duel/rooms/{id}/{hide,guess,leave,forfeit}` |
| Temps réel | WebSocket `/game/duel/ws/{room_id}` et `/game/duel/ws-lobby` |

## Règles de calcul (mode Classique)

Essais max = `⌈log2(niveau × 10)⌉` (+2 à partir du niveau 20) ; temps max = essais × 5 s. Score = `0,6 × essais + 0,3 × précision + 0,1 × temps` (chaque terme borné entre 0 et 1, temps mesuré par le serveur). Pièces = `base + bonus × score` avec `bonus = 100 × niveau` (50 × niveau dès le niveau 5) et `base = 100 + bonus` ; XP = `10 × niveau + 50 × score` ; étoiles : 1 si score ≤ 0,3, 2 si ≤ 0,5, sinon 3 (et 1 gemme).

## Temps réel (Duel)

Le Duel est synchronisé par **WebSocket** : chaque action (créer / rejoindre une salle, cacher, deviner, annuler) reste une requête HTTP validée par le serveur, puis le nouvel état est **poussé** aux deux joueurs et au lobby.

- Lancer le serveur avec la dépendance WebSocket : `pip install -r backend/requirements.txt` (installe `uvicorn[standard]`), puis `cd backend && uvicorn main:app --port 8000`. Sans cette bibliothèque, uvicorn refuse les sockets (`No supported WebSocket library detected`) ; le jeu continue alors grâce au sondage HTTP, mais sans temps réel.
- Endpoints : `ws://…/game/duel/ws/{room_id}?player_id=…` (réservé aux deux joueurs de la salle) et `ws://…/game/duel/ws-lobby`. Messages : `room`, `lobby`, `presence` (qui est connecté), `pong`.
- Côté client (`web/src/hooks/useSocket.js`) : reconnexion automatique (0,5 s doublée jusqu'à 8 s), ping toutes les 20 s, et sondage HTTP de secours (10 s si la socket marche, 1,5 s sinon).
- Limite actuelle : l'annuaire de connexions est en mémoire, donc **un seul processus serveur**. Pour en lancer plusieurs, il faudra un bus (Redis pub/sub).
- Tests : `pip install -r backend/requirements-dev.txt && pytest backend/tests` (30 tests dont le temps réel) ; e2e navigateur dans `web/e2e/`.

### Joueurs qui partent (Duel)

Réglages (variables d'environnement du serveur, en secondes) :

| Variable | Défaut | Rôle |
|---|---|---|
| `DUEL_TURN_TIMEOUT` | 90 | inactivité maximale du joueur dont c'est le tour (cacher / deviner) : au-delà, il perd par forfait |
| `DUEL_DISCONNECT_GRACE` | 30 | délai pour revenir après une coupure de socket (un simple rechargement de page ne coûte rien) |
| `DUEL_WAIT_TIMEOUT` | 600 | durée de vie d'une salle sans adversaire |
| `DUEL_SWEEP_INTERVAL` | 1 | fréquence du balayeur de délais |

- **Abandon volontaire** : `POST /game/duel/rooms/{id}/forfeit` (bouton « Abandonner », avec confirmation). L'adversaire gagne la mise (bornée par le solde du perdant).
- **Déconnexion** : l'adversaire voit une bannière avec compte à rebours ; si le joueur ne revient pas à temps, il perd par forfait. Si **les deux** sont partis, la salle est annulée et aucune pièce ne bouge.
- Le résultat manqué pendant une absence est affiché au retour (une seule fois). Motif de fin : champ `end_reason` (`solved`, `forfeit`, `disconnect`, `timeout`, `abandoned`, `expired`, `cancelled`).
- Tests : `pytest backend/tests` (45) ; e2e `web/e2e/abandon.py` (serveur lancé avec des délais courts, voir l'en-tête du script).

---

## Sécurité

**Identité.** Chaque compte a un identifiant public (`id`, visible par les autres joueurs) et un **jeton secret** renvoyé une seule fois par `POST /user/new_player`. Le serveur ne stocke que son empreinte SHA-256. Le jeton voyage dans `Authorization: Bearer …` (HTTP) ou dans le sous-protocole WebSocket (`Sec-WebSocket-Protocol: gtn.v1, <jeton>`), **jamais dans l'URL**.

- **Refus par défaut** : toute route HTTP exige un jeton valide, sauf `/health`, `/user/new_player` et `/user/claim` (liste `PUBLIC` dans `backend/routes/auth.py`). Une route ajoutée plus tard est donc protégée d'office ; un test balaie tout le schéma OpenAPI pour le vérifier.
- **On n'agit qu'en son nom** : l'identifiant fourni dans une requête doit être celui du propriétaire du jeton (sinon 403). Lire le compte d'un autre est aussi refusé.
- **Sockets** : jeton obligatoire, appartenance à la salle vérifiée, identité prise du jeton (pas de l'URL), origine contrôlée, 30 connexions max par adresse.
- **Comptes existants** (créés avant les jetons) : `POST /user/claim` donne un jeton, **une seule fois** ; le client le fait automatiquement. Tant qu'un ancien compte n'a pas été réclamé, quiconque connaît son id peut le faire : fenêtre de migration à fermer en supprimant cette route une fois les comptes migrés.
- **Récupération** : Paramètres → « Copier mon code de récupération » (c'est le jeton) puis « Restaurer un compte » sur un autre appareil. Sans ce code, un compte dont le jeton est perdu est perdu. Si le serveur ne reconnaît plus un jeton, l'appli le dit (elle ne crée jamais un nouveau compte en silence).

**Limitation de débit** (en mémoire, un seul processus) : création de comptes 10/h par adresse, réclamations 10/10 min, devinettes 120/min et par joueur, création de salles 15/min, filet général 600/min par adresse. Réponse `429` avec `Retry-After`. Taille de requête limitée à 16 Ko ; nombres, identifiants et textes bornés (jamais de 500 sur une valeur absurde).

**Navigateur** : CORS limité aux origines autorisées (sans cookies ni `credentials`), en-têtes `nosniff`, `X-Frame-Options: DENY`, `no-referrer`, `no-store` sur l'API ; **Content-Security-Policy** posée dans le build de production (scripts `self` uniquement, `connect-src` limité à l'API configurée). `frame-ancestors` doit être ajouté par le serveur qui héberge les fichiers du site (une balise `<meta>` ne le prend pas en compte). La documentation interactive (`/docs`) est désactivée par défaut.

| Variable (serveur) | Défaut | Rôle |
|---|---|---|
| `GTN_ALLOWED_ORIGINS` | – | origines supplémentaires (séparées par des virgules) pour CORS et WebSocket ; par défaut `localhost`/`127.0.0.1` sur 5173 et 4173 |
| `GTN_TRUST_PROXY` | – | `1` derrière un reverse proxy de confiance : l'adresse client est lue dans `X-Forwarded-For` |
| `GTN_RATE_LIMIT` | actif | `off` désactive la limitation (tests) |
| `GTN_MAX_WS_PER_IP` | 30 | connexions WebSocket simultanées par adresse |
| `GTN_DOCS` | – | `1` active `/docs` |
| `GTN_DATABASE_URL` | – | adresse PostgreSQL (`postgresql://…`) ; sinon fichier SQLite |
| `GTN_DB_PATH` | `main.db` | emplacement du fichier SQLite (ex. `/data/main.db` sur un volume) |
| `GTN_PROXY_HOPS` | 1 | nombre de proxys de confiance (avec `GTN_TRUST_PROXY=1`) ; `GET /whoami` sert à le vérifier |
| `GTN_NEW_ACCOUNTS_PER_HOUR` | 10 | comptes créables par heure et par adresse |

**Limites connues** : le jeton est dans `localStorage` (lisible par un script s'il y avait une faille XSS, d'où la CSP) ; limitation de débit et annuaire de sockets en mémoire (un seul processus) ; **il faut servir l'API et le site en HTTPS/WSS** en production (sinon le jeton circule en clair) ; pas de rotation ni d'expiration des jetons, pas de blocage après échecs répétés d'un même jeton (le jeton fait 256 bits, la devinette est hors de portée, mais pas la limitation de débit par adresse) ; la taille est contrôlée sur `Content-Length` seulement.

---

## État du projet et suite

Fonctionnel et testé : les quatre modes, la boutique et les power-ups, les statistiques, le temps réel et la gestion des départs, l'authentification par jeton, la PWA, l'adaptation mobile/tablette/PC.

À faire / limites connues :
- **Déploiement** : prêt à publier **gratuitement** (site sur Cloudflare Pages, serveur sur Render, base sur Neon ; variante Fly.io payante) mais pas encore en ligne : voir [DEPLOY.md](DEPLOY.md). Un seul processus serveur (limitation de débit et annuaire de sockets en mémoire) ; le serveur gratuit s'endort après 15 min d'inactivité.
- Pas encore testé sur de vrais appareils iOS / Android (installation, encoche, cadence d'images de la 3D sur GPU mobile).
- Pas de classement ni de liste d'amis, les gemmes ne servent encore à rien, une seule langue (français).
- Le jeton de compte est dans `localStorage` ; pas d'expiration ni de rotation des jetons.
