"""E2E des joueurs qui partent. Le backend doit tourner avec des delais courts:
  DUEL_DISCONNECT_GRACE=4 DUEL_TURN_TIMEOUT=12 DUEL_WAIT_TIMEOUT=8 DUEL_SWEEP_INTERVAL=0.5 uvicorn main:app --port 8000
Usage: python abandon.py <dossier-captures>"""
import os, sys, time
from playwright.sync_api import sync_playwright
B = os.environ.get("GTN_WEB", "http://127.0.0.1:4173"); API = "http://127.0.0.1:8000"; OUT = sys.argv[1]
R = []
def rec(name, ok, detail=""):
    R.append(ok); print("PASS" if ok else "FAIL", name, detail, flush=True)
def coins(pg): return pg.evaluate("fetch('%s/user/'+localStorage.getItem('id'),{headers:{Authorization:'Bearer '+localStorage.getItem('token')}}).then(r=>r.json())" % API)["coins"]
def text(pg): return pg.locator("body").inner_text()
def wait_text(pg, s, timeout=9000):
    try: pg.get_by_text(s, exact=False).first.wait_for(timeout=timeout); return True
    except Exception: return False

with sync_playwright() as p:
    b = p.chromium.launch()
    def player():
        ctx = b.new_context(viewport={"width": 1280, "height": 800}, service_workers="block"); ctx.set_default_timeout(15000)
        pg = ctx.new_page(); pg.goto(B + "/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(400)
        return ctx, pg
    def pair(name):
        """A (hote) et B (invite) dans une salle; l'hote a cache son nombre (7): B doit deviner."""
        ca, A = player(); cb, Bp = player()
        for pg in (A, Bp): pg.goto(B + "/duel"); pg.wait_for_load_state("networkidle")
        A.get_by_label("Nom de la salle").fill(name); A.get_by_role("group", name="Le nombre est entre").get_by_role("button", name="10", exact=True).click()
        A.get_by_role("group", name="Mise").get_by_role("button", name="100", exact=True).click()
        A.get_by_role("button", name="Créer la salle").click(); wait_text(Bp, name, 6000)
        Bp.get_by_role("button", name="Rejoindre").click(); wait_text(A, "Cache ton nombre")
        A.get_by_label("Ton nombre secret", exact=False).fill("7"); A.get_by_role("button", name="Cacher mon nombre").click()
        wait_text(Bp, "Trouve le nombre de", 6000)
        return ca, A, cb, Bp

    # ---- 1. abandon volontaire
    ca, A, cb, Bp = pair("Abandon")
    rec("Forfeit: a turn countdown is shown", Bp.get_by_role("timer").count() == 1 and "Ton tour" in text(Bp))
    Bp.get_by_role("button", name="Abandonner").click()
    rec("Forfeit: asks for confirmation naming the bet", wait_text(Bp, "perdre 100 pièces", 3000))
    Bp.get_by_role("button", name="Non").click()
    rec("Forfeit: 'Non' keeps playing", Bp.get_by_text("Défaite").count() == 0 and Bp.get_by_role("button", name="Abandonner").count() == 1)
    Bp.get_by_role("button", name="Abandonner").click(); Bp.get_by_role("button", name="Oui, abandonner").click()
    rec("Forfeit: quitter sees the defeat and why", wait_text(Bp, "Défaite") and wait_text(Bp, "Tu as abandonné"))
    rec("Forfeit: opponent sees the win and why", wait_text(A, "Victoire !") and wait_text(A, "a abandonné"))
    A.wait_for_timeout(1200)
    rec("Forfeit: bet paid to the opponent", (coins(A), coins(Bp)) == (600, 400), str((coins(A), coins(Bp))))
    A.screenshot(path=OUT + "/abandon-1-forfeit-win.png")
    ca.close(); cb.close()

    # ---- 2. deconnexion qui dure: banniere puis forfait
    ca, A, cb, Bp = pair("Disconnect")
    cb.close()
    rec("Disconnect: opponent gets a warning banner with a countdown", wait_text(A, "s'est déconnecté. Victoire par forfait dans", 4000))
    A.screenshot(path=OUT + "/abandon-2-banner.png")
    rec("Disconnect: after the grace period the remaining player wins", wait_text(A, "Victoire !", 9000) and wait_text(A, "déconnecté trop longtemps", 2000))
    A.wait_for_timeout(1000)
    rec("Disconnect: bet paid", coins(A) == 600, str(coins(A)))
    ca.close()

    # ---- 3. un simple rechargement de page ne fait rien perdre
    ca, A, cb, Bp = pair("Reload")
    Bp.reload(); Bp.wait_for_load_state("networkidle")
    rec("Reload: game resumes for the reloading player", wait_text(Bp, "Trouve le nombre de", 6000))
    A.wait_for_timeout(6500)                                    # bien au-dela de la periode de grace (4 s)
    rec("Reload: no forfeit and the warning is gone", A.get_by_text("Victoire !").count() == 0 and A.get_by_text("s'est déconnecté").count() == 0)
    ca.close(); cb.close()

    # ---- 4. inactivite
    ca, A, cb, Bp = pair("Inactif")                             # B doit deviner et ne fait rien
    t0 = time.time()
    rec("Timeout: idle guesser loses", wait_text(A, "Victoire !", 20000) and wait_text(A, "n'a pas joué à temps", 2000), f"{time.time()-t0:.1f}s")
    rec("Timeout: idle player is told too", wait_text(Bp, "Tu n'as pas joué à temps", 5000))
    ca.close(); cb.close()

    # ---- 5. salle oubliee
    ca, A = player(); A.goto(B + "/duel"); A.wait_for_load_state("networkidle")
    A.get_by_role("button", name="Créer la salle").click()
    rec("Expiry: waiting room closes by itself with an explanation", wait_text(A, "La salle a expiré", 14000) and A.get_by_text("Créer une salle").count() > 0)
    ca.close()

    # ---- 6. resultat manque pendant l'absence
    ca, A = player(); cb, Bp = player()
    for pg in (A, Bp): pg.goto(B + "/duel"); pg.wait_for_load_state("networkidle")
    A.get_by_label("Nom de la salle").fill("Absent"); A.get_by_role("button", name="Créer la salle").click(); wait_text(Bp, "Absent", 6000)
    Bp.get_by_role("button", name="Rejoindre").click(); wait_text(A, "Cache ton nombre")
    Bp.wait_for_timeout(600)
    state = cb.storage_state(); cb.close()                      # le navigateur de B disparait (avec son stockage local)
    rec("Away: host wins when the guest vanishes", wait_text(A, "Victoire !", 12000))
    cb2 = b.new_context(viewport={"width": 1280, "height": 800}, service_workers="block", storage_state=state); B2 = cb2.new_page()
    B2.goto(B + "/duel"); B2.wait_for_load_state("networkidle")
    rec("Away: coming back shows the defeat that happened meanwhile", wait_text(B2, "Défaite", 6000) and wait_text(B2, "déconnecté trop longtemps", 2000))
    B2.get_by_role("button", name="Retour au lobby").click()
    rec("Away: result is shown only once", wait_text(B2, "Créer une salle") and B2.get_by_text("Défaite").count() == 0)
    ca.close(); cb2.close()
    b.close()
print("TOTAL", len(R), "PASS", sum(R), "FAIL", len(R) - sum(R))
