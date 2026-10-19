"""E2E securite: jetons, migration d'anciens comptes, code de recuperation, session perdue, usurpation, CSP, debit.
Lancer le backend SANS GTN_RATE_LIMIT=off (la limitation est testee) et le relancer ensuite pour les autres scripts.
Usage: GTN_DB=/chemin/main.db python security.py <dossier-captures>"""
import os, sqlite3, sys, time
from playwright.sync_api import sync_playwright
B = os.environ.get("GTN_WEB", "http://127.0.0.1:4173"); API = "http://127.0.0.1:8000"; DB = os.environ["GTN_DB"]; OUT = sys.argv[1]
R = []
def rec(name, ok, detail=""):
    R.append(ok); print("PASS" if ok else "FAIL", name, detail, flush=True)
def db(sql, *a):
    c = sqlite3.connect(DB); r = c.execute(sql, a).fetchall(); c.commit(); c.close(); return r
def ls(pg, k): return pg.evaluate("localStorage.getItem(%r)" % k)
def text(pg): return pg.locator("body").inner_text()
def wait_text(pg, s, timeout=8000):
    try: pg.get_by_text(s, exact=False).first.wait_for(timeout=timeout); return True
    except Exception: return False
def open_settings(pg):
    pg.goto(B + "/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
    for _ in range(4): pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(250)
    pg.keyboard.press("Enter"); pg.wait_for_timeout(700)

with sync_playwright() as p:
    b = p.chromium.launch()
    def ctx(**kw):
        c = b.new_context(viewport={"width": 1280, "height": 900}, service_workers="block", **kw); c.set_default_timeout(12000)
        c.add_init_script("""window.__csp = []; document.addEventListener('securitypolicyviolation', e => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));""")
        return c

    # 1. un nouveau navigateur recoit un compte avec un jeton secret
    c1 = ctx(permissions=["clipboard-read", "clipboard-write"]); P1 = c1.new_page()
    P1.goto(B + "/"); P1.wait_for_load_state("networkidle"); P1.wait_for_timeout(800)
    id1, tok1 = ls(P1, "id"), ls(P1, "token")
    rec("New browser gets an account id and a long secret token", bool(id1) and bool(tok1) and len(tok1) >= 40)
    rec("Token is stored hashed, never in clear", db("select token_hash from player where id=?", id1)[0][0] not in (None, tok1) and len(db("select token_hash from player where id=?", id1)[0][0]) == 64)
    rec("Home shows the player (authenticated request works)", "Niv." in text(P1))
    me = P1.evaluate("async()=>fetch('%s/user/me',{headers:{Authorization:'Bearer '+localStorage.getItem('token')}}).then(r=>r.json())" % API)
    rec("The token is not echoed back by the API", "token" not in me)

    # 2. migration: un compte cree avant les jetons (id seul) reclame un jeton automatiquement
    db("insert into player(id,name,level,created_at,xp,coins,gems) values('legacy-e2e','Ancien',3,0,10,777,9)")
    c2 = ctx(); c2.add_init_script("localStorage.setItem('id','legacy-e2e')"); P2 = c2.new_page()
    P2.goto(B + "/"); P2.wait_for_load_state("networkidle"); P2.wait_for_timeout(1200)
    rec("Legacy account is migrated: it receives a token", bool(ls(P2, "token")) and ls(P2, "id") == "legacy-e2e")
    rec("Legacy progress is kept (777 coins)", wait_text(P2, "777", 3000))
    rec("Server now holds a token hash for it", db("select token_hash from player where id='legacy-e2e'")[0][0] is not None)
    c3 = ctx(); c3.add_init_script("localStorage.setItem('id','legacy-e2e')"); P3 = c3.new_page()
    P3.goto(B + "/"); P3.wait_for_load_state("networkidle"); P3.wait_for_timeout(1200)
    rec("Claiming an already-claimed id does not take it over", ls(P3, "id") != "legacy-e2e")
    c2.close(); c3.close()

    # 3. code de recuperation: copier sur un navigateur, restaurer sur un autre
    open_settings(P1)
    P1.get_by_role("button", name="Copier mon code de récupération").click(); P1.wait_for_timeout(400)
    clip = P1.evaluate("navigator.clipboard.readText()")
    rec("Copy button puts the recovery code (the token) in the clipboard", clip == tok1)
    P1.screenshot(path=OUT + "/security-1-settings.png")
    c4 = ctx(); P4 = c4.new_page(); open_settings(P4)
    id4_before = ls(P4, "id")
    P4.get_by_label("Restaurer un compte").fill("not-a-real-code"); P4.get_by_role("button", name="Restaurer", exact=True).click()
    rec("A wrong recovery code is refused and changes nothing", wait_text(P4, "Code invalide", 4000) and ls(P4, "id") == id4_before)
    P4.get_by_label("Restaurer un compte").fill(tok1); P4.get_by_role("button", name="Restaurer", exact=True).click()
    P4.wait_for_load_state("networkidle"); P4.wait_for_timeout(1500)
    rec("Right code restores the account on another browser", ls(P4, "id") == id1 and ls(P4, "token") == tok1)

    # 4. jeton refuse: on previent, on ne cree JAMAIS un compte en silence
    count_before = db("select count(*) from player")[0][0]
    P4.evaluate("localStorage.setItem('token','tampered-token')"); P4.goto(B + "/"); P4.wait_for_load_state("networkidle"); P4.wait_for_timeout(1000)
    rec("Unrecognised token shows the 'Compte non reconnu' dialog", wait_text(P4, "Compte non reconnu", 4000))
    rec("...and no account was created behind the user's back", db("select count(*) from player")[0][0] == count_before)
    P4.screenshot(path=OUT + "/security-2-session-lost.png")
    P4.get_by_label("Code de récupération").fill(tok1); P4.get_by_role("button", name="Restaurer mon compte").click()
    P4.wait_for_load_state("networkidle"); P4.wait_for_timeout(1200)
    rec("Restoring from the dialog brings the account back", ls(P4, "token") == tok1 and P4.get_by_text("Compte non reconnu").count() == 0)
    c4.close()

    # 5. usurpation depuis le navigateur: le jeton d'un autre ne permet pas d'agir pour moi
    c5 = ctx(); P5 = c5.new_page(); P5.goto(B + "/"); P5.wait_for_load_state("networkidle"); P5.wait_for_timeout(800)
    attacker_token = ls(P5, "token")
    r = P5.evaluate("""async([api, victim, token]) => {
        const h = {'Content-Type':'application/json','Authorization':'Bearer '+token};
        const out = {};
        out.rename = (await fetch(api+'/user/rename',{method:'POST',headers:h,body:JSON.stringify({player_id:victim,name:'pwned'})})).status;
        out.read = (await fetch(api+'/user/'+victim,{headers:h})).status;
        out.buy = (await fetch(api+'/shop/buy',{method:'POST',headers:h,body:JSON.stringify({playerId:victim,itemId:1})})).status;
        out.nologin = (await fetch(api+'/user/'+victim)).status;
        return out }""", [API, id1, attacker_token])
    rec("Another player's token cannot rename/read/buy for me (403)", (r["rename"], r["read"], r["buy"]) == (403, 403, 403), str(r))
    rec("No token at all is refused (401)", r["nologin"] == 401)
    rec("Victim's data untouched", db("select name from player where id=?", id1)[0][0] != "pwned")

    # 6. CSP: aucune violation pendant la navigation normale, et un script injecte est bloque
    P1.goto(B + "/shop"); P1.wait_for_load_state("networkidle"); P1.wait_for_timeout(800)
    P1.goto(B + "/duel"); P1.wait_for_load_state("networkidle"); P1.wait_for_timeout(800)
    P1.goto(B + "/classic"); P1.wait_for_load_state("networkidle"); P1.wait_for_timeout(800)
    rec("No CSP violation while using Home, Shop, Duel and Classic", P1.evaluate("window.__csp") == [], str(P1.evaluate("window.__csp")))
    P1.evaluate("""() => { const s = document.createElement('script'); s.textContent = 'window.__xss = 1'; document.body.appendChild(s) }""")
    P1.wait_for_timeout(300)
    rec("An injected inline script is blocked by the CSP", P1.evaluate("window.__xss") is None and any("script-src" in v for v in P1.evaluate("window.__csp")))
    P1.evaluate("window.__csp = []")
    P1.evaluate("fetch('https://example.com/steal').catch(()=>{})"); P1.wait_for_timeout(500)
    rec("Requests to other websites are blocked by connect-src", any("connect-src" in v for v in P1.evaluate("window.__csp")))

    # 7. limitation de debit: la creation de comptes est plafonnee
    codes = P5.evaluate("""async (api) => { const out = []; for (let i = 0; i < 16; i++) { const r = await fetch(api+'/user/new_player',{method:'POST'}); out.push([r.status, r.headers.get('retry-after')]) } return out }""", API)
    first429 = next((i for i, c in enumerate(codes) if c[0] == 429), None)
    rec("Account creation is rate limited (429 with Retry-After)", first429 is not None and codes[first429][1] is not None, f"first 429 after {first429} extra accounts")
    c5.close(); c1.close()
    b.close()
print("TOTAL", len(R), "PASS", sum(R), "FAIL", len(R) - sum(R))
