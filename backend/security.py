"""Protections transversales: limitation de debit, en-tetes de securite, taille des requetes, origines autorisees.

Limite connue: les compteurs sont en memoire (un seul processus serveur); avec plusieurs processus il faudrait un
stockage partage (Redis).
"""
import json
import os
import re
import time
from collections import defaultdict, deque

# Origines (pages web) autorisees a appeler l'API depuis un navigateur et a ouvrir des WebSockets.
DEFAULT_ORIGINS = [
    "http://localhost:5173", "http://127.0.0.1:5173",     # Vite (dev)
    "http://localhost:4173", "http://127.0.0.1:4173",     # Vite (apercu de production)
]
ALLOWED_ORIGINS = DEFAULT_ORIGINS + [o.strip() for o in os.environ.get("GTN_ALLOWED_ORIGINS", "").split(",") if o.strip()]
TRUST_PROXY = os.environ.get("GTN_TRUST_PROXY") == "1"     # derriere un reverse proxy de confiance: lire X-Forwarded-For
PROXY_HOPS = int(os.environ.get("GTN_PROXY_HOPS", 1))      # nombre de proxys de confiance devant le serveur
MAX_BODY = 16 * 1024                                       # octets

# (methode, regex du chemin, nombre max, fenetre en secondes, cle) ; cle = "ip" ou "token"
DEFAULT_RULES = [
    ("POST", r"^/user/new_player$", int(os.environ.get("GTN_NEW_ACCOUNTS_PER_HOUR", 10)), 3600, "ip"),   # creation de comptes (des testeurs sur un meme Wi-Fi partagent une adresse: augmenter si besoin)
    ("POST", r"^/user/claim$", 10, 600, "ip"),
    ("POST", r"^/game/guess$", 120, 60, "token"),
    ("POST", r"^/game/powerup$", 60, 60, "token"),
    ("POST", r"^/game/duel/host$", 15, 60, "token"),
    ("POST", r"^/game/duel/join$", 30, 60, "token"),
    ("POST", r"^/shop/buy$", 60, 60, "token"),
    ("*", r".*", 600, 60, "ip"),                              # filet general par adresse
]
MAX_WS_PER_IP = int(os.environ.get("GTN_MAX_WS_PER_IP", 30))


class RateLimiter:
    def __init__(self, rules=None, enabled=True):
        self.rules = rules or DEFAULT_RULES
        self.enabled = enabled
        self.hits = defaultdict(deque)

    def check(self, method: str, path: str, ip: str, token: str):
        """None si la requete passe, sinon le nombre de secondes a attendre."""
        if not self.enabled:
            return None
        now = time.monotonic()
        for i, (m, pattern, limit, window, scope) in enumerate(self.rules):
            if m not in ("*", method) or not re.match(pattern, path):
                continue
            key = (i, ip if scope == "ip" else (token or ip))
            q = self.hits[key]
            while q and q[0] <= now - window:
                q.popleft()
            if len(q) >= limit:
                return max(1, int(q[0] + window - now) + 1)
            q.append(now)
        if len(self.hits) > 50_000:                           # menage: on oublie les cles inactives
            for k in [k for k, v in self.hits.items() if not v]:
                del self.hits[k]
        return None


limiter = RateLimiter(enabled=os.environ.get("GTN_RATE_LIMIT") != "off")

SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"referrer-policy", b"no-referrer"),
    (b"x-frame-options", b"DENY"),
    (b"cache-control", b"no-store"),                          # reponses de l'API: ne jamais les garder en cache partage
]


def client_ip(scope) -> str:
    if TRUST_PROXY:
        for k, v in scope["headers"]:
            if k == b"x-forwarded-for":
                # Chaque proxy AJOUTE l'adresse de son client a la fin de la liste. Le debut de la liste est
                # fourni par le client (donc falsifiable): on lit l'entree ajoutee par NOTRE proxy, en partant de la fin.
                hops = [h.strip() for h in v.decode().split(",") if h.strip()]
                if len(hops) >= PROXY_HOPS:
                    return hops[-PROXY_HOPS]
    return (scope.get("client") or ("unknown", 0))[0]


def origin_allowed(origin) -> bool:
    """Une requete sans en-tete Origin (client non navigateur) est acceptee: seul un navigateur peut etre
    detourne par un site tiers, et il envoie toujours Origin sur une WebSocket."""
    return origin is None or origin in ALLOWED_ORIGINS


async def _json(send, status: int, detail: str, extra=()):
    body = json.dumps({"detail": detail}).encode()
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode()), *SECURITY_HEADERS, *extra]})
    await send({"type": "http.response.body", "body": body})


class SecurityMiddleware:
    """ASGI pur (compatible WebSocket): taille max, limitation de debit, en-tetes de securite."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope["headers"])
        if scope["method"] != "OPTIONS":
            if int(headers.get(b"content-length", b"0") or 0) > MAX_BODY:
                return await _json(send, 413, "Request too large")
            token = headers.get(b"authorization", b"").decode()[-64:]
            wait = limiter.check(scope["method"], scope["path"], client_ip(scope), token)
            if wait is not None:
                return await _json(send, 429, "Too many requests, slow down", [(b"retry-after", str(wait).encode())])

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                present = {k.lower() for k, _ in message.get("headers", [])}
                message["headers"] = list(message.get("headers", [])) + [h for h in SECURITY_HEADERS if h[0] not in present]
            await send(message)

        await self.app(scope, receive, send_with_headers)
