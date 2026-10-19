"""Test de fumee d'un site DEJA en ligne (ou local): `python smoke.py https://mon-site.pages.dev`.
Ne touche pas a la base: il cree deux comptes jetables et joue un duel complet entre deux navigateurs.
Verifie ce qui casse typiquement au premier deploiement: HTTPS/WSS, CORS, origines, liens directs, CSP, PWA."""
import sys
from playwright.sync_api import sync_playwright
SITE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4173").rstrip("/")
R = []
def rec(name, ok, detail=""):
    R.append(ok); print("PASS" if ok else "FAIL", name, detail, flush=True)
def wait_text(pg, s, timeout=15000):
    try: pg.get_by_text(s, exact=False).first.wait_for(timeout=timeout); return True
    except Exception: return False

with sync_playwright() as p:
    b = p.chromium.launch()
    def player():
        ctx = b.new_context(viewport={"width": 1280, "height": 850}); ctx.set_default_timeout(20000)
        ctx.add_init_script("window.__csp=[]; document.addEventListener('securitypolicyviolation', e => window.__csp.push(e.violatedDirective+' '+e.blockedURI))")
        pg = ctx.new_page(); logs = []
        pg.on("console", lambda m: logs.append(m.text[:140]) if m.type == "error" else None)
        pg.on("pageerror", lambda e: logs.append("PAGEERROR " + str(e)[:140]))
        return ctx, pg, logs

    ca, A, la = player()
    A.goto(SITE + "/"); A.wait_for_load_state("networkidle"); A.wait_for_timeout(1500)
    rec("Home loads and the player is created through the API (CORS + HTTPS work)", wait_text(A, "Niv.") and bool(A.evaluate("localStorage.getItem('token')")))
    rec("Web app manifest is served", A.evaluate("fetch('/manifest.webmanifest').then(r => r.ok)"))
    A.reload(); A.wait_for_load_state("networkidle"); A.wait_for_timeout(1500)
    rec("Service worker is active (installable app, works offline)", A.evaluate("navigator.serviceWorker.getRegistration().then(r => !!r && !!r.active)"))
    A.goto(SITE + "/duel"); A.wait_for_load_state("networkidle")
    rec("A direct link (/duel) opens the app, not a 404", wait_text(A, "Créer une salle"))
    rec("Real-time connection works ('En direct' = WebSocket accepted)", wait_text(A, "En direct", 12000))
    rec("No Content-Security-Policy violation and no console error", A.evaluate("window.__csp") == [] and la == [], str(A.evaluate("window.__csp")) + str(la[:2]))

    cb, B, lb = player()
    B.goto(SITE + "/duel"); B.wait_for_load_state("networkidle"); wait_text(B, "En direct")
    A.get_by_label("Nom de la salle").fill("Test de fumee")
    A.get_by_role("group", name="Mise").get_by_role("button", name="0", exact=True).click()
    A.get_by_role("group", name="Le nombre est entre").get_by_role("button", name="10", exact=True).click()
    A.get_by_role("button", name="Créer la salle").click()
    rec("A second player sees the new room live", wait_text(B, "Test de fumee", 10000))
    B.get_by_role("button", name="Rejoindre").click()
    rec("Joining starts the game for both players", wait_text(A, "Cache ton nombre", 10000))
    A.get_by_label("Ton nombre secret", exact=False).fill("7"); A.get_by_role("button", name="Cacher mon nombre").click()
    rec("Guesser gets the game panel in real time", wait_text(B, "Trouve le nombre de", 10000))
    def guess(pg, n): pg.locator("input[type=number]").first.fill(str(n)); pg.locator("button.guess-button").click()
    guess(B, 7)
    rec("Finding the number moves to round 2", wait_text(B, "Cache ton nombre", 12000))
    B.get_by_label("Ton nombre secret", exact=False).fill("4"); B.get_by_role("button", name="Cacher mon nombre").click()
    wait_text(A, "Trouve le nombre de", 10000); guess(A, 4)
    rec("The duel ends with a result for both players (tie: host wins)", wait_text(A, "Victoire !", 12000) and wait_text(B, "Défaite", 12000))
    rec("No CSP violation or console error during the whole game", A.evaluate("window.__csp") == [] and B.evaluate("window.__csp") == [] and la == [] and lb == [], str((la + lb)[:2]))

    A.context.set_offline(True); A.goto(SITE + "/"); A.wait_for_timeout(1500)
    rec("Offline reload still shows the app with an offline notice", wait_text(A, "Hors ligne", 5000))
    A.context.set_offline(False)
    # serveur gratuit endormi: on simule une premiere reponse tres lente (6,5 s) et on verifie le message
    cw = b.new_context(viewport={"width": 1280, "height": 850}); cw.set_default_timeout(20000)
    cw.add_init_script("""const f = window.fetch.bind(window); window.fetch = (u, o) => String(u).endsWith('/user/new_player') ? new Promise(r => setTimeout(() => r(f(u, o)), 6500)) : f(u, o)""")
    W = cw.new_page(); W.goto(SITE + "/")
    rec("A slow server shows 'Le serveur se réveille' after ~5 s", wait_text(W, "Le serveur se réveille", 9000))
    W.wait_for_timeout(3500)
    rec("...and the message disappears once the server answers", W.get_by_text("Le serveur se réveille").count() == 0 and bool(W.evaluate("localStorage.getItem('token')")))
    cw.close()
    ca.close(); cb.close(); b.close()
print("TOTAL", len(R), "PASS", sum(R), "FAIL", len(R) - sum(R))
sys.exit(0 if all(R) else 1)
