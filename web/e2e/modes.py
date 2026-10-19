"""E2E Duel (deux joueurs dans deux navigateurs) et Mode Infini.
Usage: GTN_DB=/chemin/main.db python modes.py <dossier-captures>"""
import os, re, sqlite3, sys, time
from playwright.sync_api import sync_playwright
B = os.environ.get("GTN_WEB", "http://127.0.0.1:4173"); API = "http://127.0.0.1:8000"; DB = os.environ["GTN_DB"]; OUT = sys.argv[1]
R = []
def rec(name, ok, detail=""):
    R.append(ok); print("PASS" if ok else "FAIL", name, detail, flush=True)
def db(sql, *a):
    c = sqlite3.connect(DB); r = c.execute(sql, a).fetchall(); c.commit(); c.close(); return r
def coins(pg): return pg.evaluate("fetch('%s/user/'+localStorage.getItem('id'),{headers:{Authorization:'Bearer '+localStorage.getItem('token')}}).then(r=>r.json())" % API)["coins"]
def text(pg): return pg.locator("body").inner_text()
def wait_text(pg, s, timeout=9000):
    try: pg.get_by_text(s, exact=False).first.wait_for(timeout=timeout); return True
    except Exception: return False

with sync_playwright() as p:
    b = p.chromium.launch()
    def player(w=1280, h=800):
        ctx = b.new_context(viewport={"width": w, "height": h}, service_workers="block"); ctx.set_default_timeout(15000); pg = ctx.new_page()
        pg.goto(B + "/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(500)
        return ctx, pg
    errs = []
    ctxA, A = player(); ctxB, Bp = player()
    for pg in (A, Bp): pg.on("pageerror", lambda e: errs.append(str(e)[:150]))

    # ---------------- DUEL ----------------
    A.goto(B + "/duel"); A.wait_for_load_state("networkidle")
    Bp.goto(B + "/duel"); Bp.wait_for_load_state("networkidle")
    rec("Duel: lobby shows create form", wait_text(A, "Créer une salle"))
    rec("Duel: lobby socket is live ('En direct')", wait_text(A, "En direct", 4000) and wait_text(Bp, "En direct", 4000))
    A.get_by_label("Nom de la salle").fill("Duel e2e")
    A.get_by_role("group", name="Mise").get_by_role("button", name="100", exact=True).click()
    A.get_by_role("group", name="Le nombre est entre").get_by_role("button", name="10", exact=True).click()
    t0 = time.time()
    A.get_by_role("button", name="Créer la salle").click()
    rec("Duel: host waits for an opponent", wait_text(A, "En attente d'un adversaire"))
    seen = wait_text(Bp, "Duel e2e", 6000); dt = time.time() - t0
    rec("Duel: guest sees the new room pushed live (< 0.8 s)", seen and dt < 0.8, f"{dt*1000:.0f} ms")
    A.screenshot(path=OUT + "/duel-1-waiting.png"); Bp.screenshot(path=OUT + "/duel-2-lobby.png")
    Bp.get_by_role("button", name="Rejoindre").click()
    rec("Duel: guest waits while the host hides", wait_text(Bp, "choisit son nombre"))
    rec("Duel: host is asked to hide a number", wait_text(A, "Cache ton nombre"))
    rec("Duel: room header shows the live connection and opponent online", wait_text(A, "En direct", 3000) and A.get_by_label("adversaire connecté").count() == 1)

    # un mauvais nombre est refuse par le serveur, un bon est accepte
    A.get_by_label("Ton nombre secret", exact=False).fill("99"); A.get_by_role("button", name="Cacher mon nombre").click()
    rec("Duel: out-of-range secret is rejected with a message", wait_text(A, "Choisis un nombre entre 1 et 10", 4000) and A.get_by_text("Cache ton nombre").count() == 1)
    A.get_by_label("Ton nombre secret", exact=False).fill("7")
    t0 = time.time(); A.get_by_role("button", name="Cacher mon nombre").click()
    seen = wait_text(Bp, "Trouve le nombre de"); dt = time.time() - t0
    rec("Duel: guest gets the guess panel pushed live (< 0.8 s)", seen and dt < 0.8, f"{dt*1000:.0f} ms")
    rec("Duel: host watches the opponent search", wait_text(A, "cherche ton nombre"))
    Bp.screenshot(path=OUT + "/duel-3-guess.png")

    def guess(pg, n):
        pg.locator("input[type=number]").first.fill(str(n)); pg.locator("button.guess-button").click(); pg.wait_for_timeout(500)
    t0 = time.time(); guess(Bp, 3)
    rec("Duel: wrong guess gives the 'Trop petit' hint", "Trop petit" in text(Bp))
    seen = wait_text(A, "Dernière proposition : trop petite"); dt = time.time() - t0
    rec("Duel: host sees the opponent's guess live (< 1 s incl. the 0.5 s test pause)", seen and dt < 1.0, f"{dt*1000:.0f} ms")
    A.screenshot(path=OUT + "/duel-4-watch.png")

    # reprise apres rechargement de page (l'etat vient du serveur)
    Bp.reload(); Bp.wait_for_load_state("networkidle")
    rec("Duel: reload resumes the running game", wait_text(Bp, "Trouve le nombre de", 6000))
    guess(Bp, 7)
    rec("Duel: finding the number hands over to round 2", wait_text(Bp, "Cache ton nombre", 8000))
    rec("Duel: host waits while the guest hides (round 2)", wait_text(A, "choisit son nombre", 6000))
    Bp.get_by_label("Ton nombre secret", exact=False).fill("4"); Bp.get_by_role("button", name="Cacher mon nombre").click()
    rec("Duel: host (round 2) sees the guess panel", wait_text(A, "Trouve le nombre de", 6000))
    guess(A, 4)                                    # 1 essai pour l'hote, 2 pour l'invite -> l'hote gagne
    rec("Duel: winner sees the victory screen", wait_text(A, "Victoire !", 9000))
    rec("Duel: loser sees the defeat screen", wait_text(Bp, "Défaite", 9000))
    A.wait_for_timeout(1200)
    A.screenshot(path=OUT + "/duel-5-result.png")
    rec("Duel: bet moved from loser to winner", (coins(A), coins(Bp)) == (600, 400), str((coins(A), coins(Bp))))
    A.get_by_role("button", name="Retour au lobby").click()
    rec("Duel: back to the lobby after the result", wait_text(A, "Créer une salle"))

    # annuler une salle en attente
    A.get_by_role("button", name="Créer la salle").click(); wait_text(A, "En attente d'un adversaire")
    A.get_by_role("button", name="Annuler la salle").click()
    rec("Duel: host can cancel a waiting room", wait_text(A, "Créer une salle"))
    Bp.get_by_role("button", name="Retour au lobby").click(); Bp.wait_for_timeout(3500)
    rec("Duel: cancelled room disappears for others", "Salle de" not in text(Bp) or Bp.get_by_role("button", name="Rejoindre").count() == 0)

    # ---------------- PRESENCE ET REPLI ----------------
    ctxD, D = player(); ctxE, E = player()
    D.goto(B + "/duel"); D.wait_for_load_state("networkidle"); E.goto(B + "/duel"); E.wait_for_load_state("networkidle")
    D.get_by_role("button", name="Créer la salle").click(); wait_text(D, "En attente d'un adversaire")
    wait_text(E, "Rejoindre", 6000); E.get_by_role("button", name="Rejoindre").click()
    ok = wait_text(D, "Cache ton nombre")
    try: D.get_by_label("adversaire connecté").wait_for(timeout=3000)
    except Exception: ok = False
    rec("Presence: host sees the guest online", ok)
    ctxE.close()                                      # le navigateur de l'invite disparait
    seen = False
    for _ in range(40):
        if D.get_by_label("adversaire hors ligne").count() == 1: seen = True; break
        D.wait_for_timeout(100)
    rec("Presence: host sees the guest go offline within 4 s", seen)

    # sockets bloquees (proxy, pare-feu...): toute connexion echoue tout de suite; le jeu doit continuer via le sondage HTTP
    BLOCK = "window.WebSocket = class { static OPEN = 1; constructor() { setTimeout(() => this.onclose && this.onclose({ code: 1006 }), 20) } send() {} close() {} }"
    ctxF, F = player(); ctxG, G = player()
    for c in (ctxF, ctxG): c.add_init_script(BLOCK)
    F.goto(B + "/duel"); F.wait_for_load_state("networkidle"); G.goto(B + "/duel"); G.wait_for_load_state("networkidle")
    F.get_by_role("button", name="Créer la salle").click(); wait_text(F, "En attente d'un adversaire")
    rec("Fallback: UI says it is reconnecting when sockets are blocked", wait_text(F, "Reconnexion", 4000))
    rec("Fallback: lobby still lists rooms via polling", wait_text(G, "Rejoindre", 7000))
    G.get_by_role("button", name="Rejoindre").click()
    rec("Fallback: host still notified of the guest via polling", wait_text(F, "Cache ton nombre", 5000))
    F.get_by_label("Ton nombre secret", exact=False).fill("5"); F.get_by_role("button", name="Cacher mon nombre").click()
    rec("Fallback: guest still gets the guess panel via polling", wait_text(G, "Trouve le nombre de", 5000))
    for c in (ctxD, ctxF, ctxG): c.close()

    # ---------------- INFINI ----------------
    ctxC, C = player(); C.goto(B + "/endless"); C.wait_for_load_state("networkidle")
    rec("Endless: setup screen", wait_text(C, "Mode Infini"))
    C.get_by_role("button", name="50", exact=True).click(); C.get_by_role("button", name="Commencer").click()
    rec("Endless: stage 1 starts, bet debited", wait_text(C, "Palier 1") and coins(C) == 450, str(coins(C)))
    n = db("select number from sessions where type='endless' order by started_time desc limit 1")[0][0]
    wrong = 1 if n != 1 else 2
    def guessC(x): C.locator("input[type=number]").first.fill(str(x)); C.locator("button.guess-button").click(); C.wait_for_timeout(450)
    guessC(wrong); guessC(n)
    rec("Endless: stage cleared with the reward (50 x 1.25 = 62)", wait_text(C, "Palier 1 réussi", 6000) and wait_text(C, "+62", 3000))
    rec("Endless: reward credited (450 + 62)", coins(C) == 512, str(coins(C)))
    C.screenshot(path=OUT + "/endless-1-cleared.png")
    C.get_by_role("button", name="Continuer").click()
    rec("Endless: stage 2 re-bets the winnings", wait_text(C, "Palier 2") and wait_text(C, "Mise 62") and coins(C) == 450, str(coins(C)))
    n2 = db("select number from sessions where type='endless' order by started_time desc limit 1")[0][0]
    rec("Endless: stage 2 range grows (1..20)", C.locator("input[type=number]").first.get_attribute("placeholder") == "entre 1 et 20")
    C.screenshot(path=OUT + "/endless-2-stage2.png")
    for x in [v for v in range(1, 21) if v != n2][:5]: guessC(x)
    rec("Endless: out of attempts ends the run", wait_text(C, "Perdu au palier 2", 6000))
    rec("Endless: lost stake is gone (450)", coins(C) == 450, str(coins(C)))
    C.screenshot(path=OUT + "/endless-3-lost.png")
    C.get_by_role("button", name="Rejouer").click()
    rec("Endless: replay returns to the setup", wait_text(C, "Ta mise"))
    rec("No page errors", not errs, str(errs[:2]))
    b.close()
print("TOTAL", len(R), "PASS", sum(R), "FAIL", len(R) - sum(R))
