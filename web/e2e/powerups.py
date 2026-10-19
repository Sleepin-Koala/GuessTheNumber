"""E2E des power-ups: boutique -> inventaire -> bonus avant depart -> utilisation en partie (Classic + Discovery).
Usage: GTN_DB=/chemin/main.db python powerups.py <dossier-captures>"""
import os, sqlite3, sys
from playwright.sync_api import sync_playwright
B = os.environ.get("GTN_WEB", "http://127.0.0.1:4173"); API = "http://127.0.0.1:8000"; DB = os.environ["GTN_DB"]; OUT = sys.argv[1]
R = []
def rec(name, ok, detail=""):
    R.append(ok); print("PASS" if ok else "FAIL", name, detail, flush=True)
def db(sql, *a):
    c = sqlite3.connect(DB); r = c.execute(sql, a).fetchall(); c.commit(); c.close(); return r
def secret(): return db("select number from sessions order by started_time desc limit 1")[0][0]
def held(pid, item):
    r = db("select amount from hold where playerId=? and itemId=?", pid, item); return r[0][0] if r else 0

with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 1280, "height": 800}, service_workers="block"); pg = ctx.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)[:150]))
    pg.goto(B + "/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(600)
    pid = pg.evaluate("localStorage.getItem('id')")

    # 1. boutique: un achat apparait dans l'inventaire
    pg.goto(B + "/shop"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
    pg.get_by_role("button", name="Indices").click(); pg.wait_for_timeout(400)
    pg.get_by_role("button", name="Acheter").nth(1).click(); pg.wait_for_timeout(1000)    # Premier (120)
    rec("Shop: purchase shows an owned badge", pg.get_by_label("1 en stock").count() == 1)
    rec("Shop: inventory endpoint agrees", pg.evaluate("fetch('%s/shop/inventory/'+localStorage.getItem('id'),{headers:{Authorization:'Bearer '+localStorage.getItem('token')}}).then(r=>r.json())" % API)["items"].get("5") == 1)

    # 2. donne 2 de chaque objet pour la suite (le reste de la boutique est deja teste)
    for i in range(1, 9):
        db("insert into hold(playerId,itemId,amount) select ?,?,0 where not exists(select 1 from hold where playerId=? and itemId=?)", pid, i, pid, i)
        db("update hold set amount=2 where playerId=? and itemId=?", pid, i)

    # 3. Classic: bonus avant depart
    pg.goto(B + "/classic"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1200)
    pg.get_by_text("1-10").first.click(); pg.wait_for_timeout(700)
    rec("Pre-game: 3 bonuses with stock counts", pg.get_by_text("×2").count() == 3)
    for label in ("+3 essais", "Indice", "Rage"): pg.get_by_role("button", name=label).click()
    pg.screenshot(path=OUT + "/powerups-1-pregame.png")
    pg.get_by_text("GO !").click(); pg.wait_for_timeout(2000)
    body = pg.locator("body").inner_text()
    rec("Pre-game: +3 essais applied", "+3 essais" in body and "7/7" in body.replace(" ", ""), "attempt bar")
    rec("Pre-game: Rage applied", "Pièces x2 si tu gagnes" in body)
    rec("Pre-game: Indice armed", "Indice armé" in body)
    rec("Pre-game: stock consumed (life 2->1, rage 2->1, advisor still 2)", (held(pid,3), held(pid,8), held(pid,4)) == (1,1,2), str((held(pid,3), held(pid,8), held(pid,4))))

    # 4. outils en partie
    tray = lambda n: pg.get_by_label(f"{n}, 2 en stock")
    rec("Tray: shows owned items, not the armed advisor or Rage", tray("Nombre Pair").count()==1 and tray("Scan").count()==1 and tray("Ralenti").count()==1 and pg.get_by_label("Conseiller IA, 2 en stock").count()==0 and pg.get_by_label("Multiplicateur x2, 1 en stock").count()==0)
    n = secret()
    pg.get_by_label("Ralenti, 2 en stock").click(); pg.wait_for_timeout(700)
    rec("Slow: clock extended message", "secondes" in pg.locator("body").inner_text())
    tray("Nombre Pair").click(); pg.wait_for_timeout(700)
    rec("Parity tells the truth", ("Le nombre est " + ("pair" if n % 2 == 0 else "impair")) in pg.locator("body").inner_text())
    rec("Parity item consumed and hidden", held(pid,1)==1 and pg.get_by_label("Nombre Pair, 1 en stock").count()==0)
    # 3 erreurs -> le conseil de l'IA arrive tout seul
    for w in [x for x in range(1, 11) if x != n][:3]:
        pg.locator("input[type=number]").first.fill(str(w)); pg.locator("button.guess-button").click(); pg.wait_for_timeout(500)
    pg.wait_for_timeout(700)
    rec("Advisor fires after 3 wrong guesses", "Conseil : essaie" in pg.locator("body").inner_text())
    rec("Advisor consumed exactly once", held(pid,4)==1, str(held(pid,4)))
    pg.screenshot(path=OUT + "/powerups-2-ingame.png")
    pg.locator("input[type=number]").first.fill(str(n)); pg.locator("button.guess-button").click(); pg.wait_for_timeout(2200)
    rec("Win with bonuses: reward screen", pg.get_by_text("terminé").count() > 0)
    pg.screenshot(path=OUT + "/powerups-3-win.png")

    # 5. Discovery: seulement les power-ups qui ont du sens
    pg.goto(B + "/discovery"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
    pg.get_by_text("JOUER").click(); pg.wait_for_timeout(1500)
    d = lambda n_: pg.get_by_label(n_, exact=False).count()
    rec("Discovery tray: reveals yes, life/slow no", d("Scan,")==1 and d("Premier,")==1 and d("Vie bonus,")==0 and d("Ralenti,")==0 and d("Multiplicateur")==0)
    pg.get_by_label("Scan,", exact=False).click(); pg.wait_for_timeout(700)
    rec("Discovery: scan gives a range containing the answer", True if "Il est entre" in pg.locator("body").inner_text() else False)
    import re
    m = re.search(r"Il est entre (\d+) et (\d+)", pg.locator("body").inner_text()); n2 = secret()
    rec("Discovery: range is correct", bool(m) and int(m.group(1)) <= n2 <= int(m.group(2)), m.group(0) if m else "")
    pg.screenshot(path=OUT + "/powerups-4-discovery.png")
    rec("No page errors", not errs, str(errs[:2]))
    b.close()
print("TOTAL", len(R), "PASS", sum(R), "FAIL", len(R)-sum(R))
