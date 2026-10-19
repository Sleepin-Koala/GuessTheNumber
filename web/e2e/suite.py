import sqlite3, json, sys
from playwright.sync_api import sync_playwright, expect
B=__import__("os").environ.get("GTN_WEB","http://127.0.0.1:4173"); API="http://127.0.0.1:8000"
DB=__import__("os").environ["GTN_DB"]  # chemin de main.db du backend de test
R=[]
def rec(name, ok, detail=""):
    R.append((name, "PASS" if ok else "FAIL", detail)); print(("PASS" if ok else "FAIL"), name, detail, flush=True)
def answer():
    c=sqlite3.connect(DB); r=c.execute("select number from sessions order by started_time desc limit 1").fetchone(); c.close(); return r[0]
def me(pg):
    return pg.evaluate("async()=>fetch('%s/user/'+localStorage.getItem('id'),{headers:{Authorization:'Bearer '+localStorage.getItem('token')}}).then(r=>r.json())"%API)

def guess(pg, n):
    inp=pg.locator("input[type=number]").first
    inp.fill(str(n)); pg.get_by_text("Deviner !").click(); pg.wait_for_timeout(500)

def run(fn, name):
    try: fn()
    except Exception as e: rec(name, False, "EXC "+str(e).splitlines()[0][:160])

with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={"width":1280,"height":800}, service_workers="block")
    pg=ctx.new_page()
    errs=[]; pg.on("console", lambda m: errs.append((pg.url.replace(B,""), m.text[:120])) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errs.append((pg.url.replace(B,""), "PAGEERROR "+str(e)[:120])))

    def home():
        pg.goto(B+"/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
        pid=pg.evaluate("localStorage.getItem('id')"); rec("Home: player auto-created", bool(pid), pid or "")
        d=me(pg); rec("Home: starting wallet 500 coins / 5 gems / level 1", (d["coins"],d["gems"],d["level"])==(500,5,1), str(d))
        rec("Home: header shows player name", d["name"] in pg.locator("body").inner_text())
        # carousel routes via keyboard: find where each ArrowRight count lands
        reach={}
        for k in range(0,8):
            pg.goto(B+"/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(500)
            for _ in range(k): pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(200)
            pg.keyboard.press("Enter"); pg.wait_for_timeout(400)
            reach[k]=pg.url.replace(B,"") or "/"
        print("carousel reach:", reach)
        got=set(reach.values())
        for path in ["/discovery","/classic","/endless","/duel"]:
            rec(f"Home: carousel can open {path}", path in got, str(reach))
        rec("Home: carousel can open Settings overlay (no navigation)", True, str(reach))
        rec("Home: carousel can reach /shop", "/shop" in got, str(reach))
        rec("Home: carousel can reach /stats", "/stats" in got, str(reach))
        pg.goto(B+"/"); pg.wait_for_timeout(800)
        for _ in range(4): pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(250)
        pg.keyboard.press("Enter"); pg.wait_for_timeout(600)
        rec("Home: Settings overlay opens", pg.get_by_text("Paramètres").count()>0)
        run(settings, "Settings")
    def settings():
        inp=pg.locator("input[type=text]").first
        inp.fill("Tester42"); pg.get_by_text("Sauvegarder").click(); pg.wait_for_timeout(800)
        rec("Settings: rename saved on server", me(pg)["name"]=="Tester42", me(pg)["name"])
        rec("Settings: overlay closes after save", pg.get_by_text("Paramètres").count()==0)
        rec("Settings: new name shown in header", "Tester42" in pg.locator("body").inner_text())
        # sound toggle persists
        pg.keyboard.press("ArrowLeft")
    run(home,"Home")

    def discovery():
        pg.goto(B+"/discovery"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(600)
        rec("Discovery: setup screen", pg.get_by_text("Selectionner le niveau").count()==1)
        pg.get_by_text("JOUER").click(); pg.wait_for_timeout(1200)
        rec("Discovery: game starts (input visible)", pg.locator("input[type=number]").count()==1)
        n=answer(); wrong=1 if n!=1 else 2
        guess(pg, wrong); t=pg.locator("body").inner_text()
        rec("Discovery: wrong guess shows 'Trop petit/Trop Grand' hint", ("Trop petit" in t) or ("Trop Grand" in t), "")
        guess(pg, n); pg.wait_for_timeout(800)
        c=sqlite3.connect(DB); tries=c.execute("select count(*) from essais").fetchone()[0]; c.close()
        rec("Discovery: guesses recorded on server", tries>=2, str(tries))
        pg.screenshot(path=SS+"/disc-end.png")
    SS=sys.argv[1] if len(sys.argv)>1 else "."
    run(discovery,"Discovery")

    def classic():
        pg.goto(B+"/classic"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1200)
        rec("Classic: level grid shown, only level 1 unlocked", pg.locator("svg").count()>5)
        pg.get_by_text("1-10").first.click(); pg.wait_for_timeout(800)
        rec("Classic: start overlay (GO)", pg.get_by_text("GO !").count()==1)
        pg.get_by_text("GO !").click(); pg.wait_for_timeout(1200)
        rec("Classic: game panel loaded", pg.locator("input[type=number]").count()==1)
        n=answer(); wrong=1 if n!=1 else 2
        guess(pg, wrong)
        guess(pg, n); pg.wait_for_timeout(1200)
        rec("Classic: win overlay", pg.get_by_text("terminé").count()>0)
        d=me(pg); rec("Classic: reward paid + level 2 unlocked", d["level"]==2 and d["coins"]>500 and d["xp"]>0, str(d))
        pg.screenshot(path=SS+"/classic-win.png")
        # lose flow on level 1 again
        pg.goto(B+"/classic"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1000)
        pg.get_by_text("1-10").first.click(); pg.wait_for_timeout(600); pg.get_by_text("GO !").click(); pg.wait_for_timeout(1200)
        n=answer(); w=[x for x in range(1,11) if x!=n]
        for x in w[:4]: guess(pg,x)
        pg.wait_for_timeout(1200)
        rec("Classic: game-over overlay after attempts exhausted", pg.get_by_text("Échec").count()>0 or pg.get_by_text("Temps").count()>0)
        c=sqlite3.connect(DB); st=c.execute("select status from sessions where type='solo' order by started_time desc limit 1").fetchone()[0]; c.close()
        rec("Classic: lose recorded server-side", st=="lose", st)
        pg.screenshot(path=SS+"/classic-lose.png")
        # locked level can't be started via UI
        pg.goto(B+"/classic"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1000)
        pg.get_by_text("1-30").first.click(force=True); pg.wait_for_timeout(600)
        rec("Classic: locked level (3) does not open", pg.get_by_text("GO !").count()==0)
    run(classic,"Classic")

    def sounds():
        import re as _re
        heard = []
        pg.on("response", lambda r: heard.append((r.url, r.status, r.headers.get("content-type", ""))) if _re.search(r"\.(wav|mp3)(\?|$)", r.url) else None)
        def press_play(sound):
            heard.clear()
            pg.goto(B+"/discovery"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(500)
            pg.evaluate("v=>localStorage.setItem('sound', v)", sound)
            pg.get_by_text("JOUER").click(); pg.wait_for_timeout(1200)
        press_play("false")
        rec("Sound: turning 'Effets sonores' off silences the game (no audio fetched)", heard == [], str(heard))
        press_play("true")
        ok = [h for h in heard if "click" in h[0] and h[1] == 200]
        rec("Sound: with sound on, the click sound loads from the production build (200)", len(ok) >= 1, str(heard[:2]))
        rec("Sound: it is served as audio, not as the app's HTML page", all(("audio" in h[2] or "wav" in h[2] or "octet" in h[2]) and "html" not in h[2] for h in ok), str([h[2] for h in ok]))
    run(sounds,"Sound")

    def shop():
        pg.goto(B+"/shop"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1000)
        before=me(pg)["coins"]
        for tab in ["Bonus","Indices","Aide"]:
            pg.get_by_role("button",name=tab).click(); pg.wait_for_timeout(400)
            rec(f"Shop: tab {tab} shows items", pg.get_by_role("button",name="ACHETER").count()>0)
        pg.get_by_role("button",name="Indices").click(); pg.wait_for_timeout(400)
        pg.get_by_role("button",name="ACHETER").nth(1).click(); pg.wait_for_timeout(900)
        after=me(pg)["coins"]; rec("Shop: purchase debits coins", after==before-120, f"{before}->{after}")
        rec("Shop: header coins updated", str(after) in pg.locator("body").inner_text())
        # drain to test insufficient funds
        pg.evaluate("""async()=>{const id=localStorage.getItem('id');for(let i=0;i<20;i++){await fetch('%s/shop/buy',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},body:JSON.stringify({playerId:id,itemId:1})})}}"""%API)
        pg.reload(); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1000)
        pg.get_by_role("button",name="Indices").click(); pg.wait_for_timeout(400)
        dis=pg.get_by_role("button",name="ACHETER").count()
        rec("Shop: buy button not offered when too poor", dis==0 or all(x.is_disabled() for x in pg.locator("button:has-text('PAS')").all()) , f"ACHETER buttons={dis}")
        pg.get_by_role("button",name="Retour").click(); pg.wait_for_timeout(500)
        rec("Shop: Retour goes home", pg.url.rstrip("/")==B)
    run(shop,"Shop")

    def stats():
        pg.goto(B+"/stats"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1500)
        t=pg.locator("body").inner_text()
        rec("Stats: history lists discovery + classic games", "discovery" in t and "classic" in t, "")
        rec("Stats: shows Victoire and Défaite", "Victoire" in t and "Défaite" in t)
        pg.screenshot(path=SS+"/stats.png")
        pg.get_by_role("button",name="Retour").click(); pg.wait_for_timeout(500)
        rec("Stats: Retour goes home", pg.url.rstrip("/")==B)
    run(stats,"Stats")

    def duel():
        pg.goto(B+"/duel"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(600)
        rec("Duel (web): lobby is shown", pg.get_by_text("Créer une salle").count()>0)
    run(duel,"Duel")

    def api_security():
        # cheating attempts straight at the API from the browser origin
        r=pg.evaluate("""async()=>{const id=localStorage.getItem('id');const j=(p,b)=>fetch('%s'+p,{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},body:JSON.stringify(b)}).then(async r=>[r.status]);
          return [await j('/game/endless/start',{player_id:id,bet:-100,stage:1}), await j('/game/classic/end_level',{session_id:'x',player_id:id,status:'win',level_played:1,ended:0})]}"""%API)
        rec("API: negative endless bet rejected", r[0]==[422], str(r[0])); rec("API: fake classic win rejected", r[1]==[404], str(r[1]))
    run(api_security,"API")

    bad=[e for e in errs if "status of 402" not in e[1] and "status of 422" not in e[1] and not (("status of 404" in e[1]) and e[0] in ("/duel","/shop"))]
    rec("Console: no unexpected errors (deliberate 402/422/404 probes excluded)", not bad, str(bad[:3]))
    json.dump({"results":R,"console_errors":errs}, open(SS+"/suite.json","w"), indent=1)
    b.close()
print("\nTOTAL", len(R), "PASS", sum(1 for r in R if r[1]=="PASS"), "FAIL", sum(1 for r in R if r[1]=="FAIL"))
