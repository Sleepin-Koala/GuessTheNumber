import json, sys, sqlite3
from playwright.sync_api import sync_playwright
B="http://127.0.0.1:4173"; OUT=sys.argv[1]; TAG=sys.argv[2] if len(sys.argv)>2 else "run"
VPS=[("360x640",360,640),("390x844",390,844),("430x932",430,932),("768x1024",768,1024),("1024x768",1024,768),("1280x800",1280,800),("1920x1080",1920,1080),("844x390-landscape",844,390)]
PAGES=["/","/discovery","/classic","/shop","/stats","/duel","/endless","classic-game","discovery-game","settings"]
JS_AUDIT="""()=>{
 const W=innerWidth,H=innerHeight; const out={scrollW:document.documentElement.scrollWidth,W,H,scrollH:document.documentElement.scrollHeight,off:[],small:[],smallInputs:[]};
 const clipped=(el)=>{for(let p=el.parentElement;p&&p!==document.body;p=p.parentElement){const o=getComputedStyle(p);if(/(hidden|clip|auto|scroll)/.test(o.overflowX)){const r=p.getBoundingClientRect();if(r.right<=W+1&&r.left>=-1)return true}}return false};
 for(const el of document.querySelectorAll('body *')){const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden'||cs.position==='fixed'&&false)continue;
   const r=el.getBoundingClientRect(); if(r.width<2||r.height<2)continue;
   if((r.right>W+2||r.left<-2)&&!clipped(el)&&!el.closest('svg')&&el.tagName!=='svg'&&cs.opacity!=='0'){const bg=el.closest('[class*=absolute],[class*=fixed],[class*=-z-]'); if(out.off.length<6)out.off.push(el.tagName+'.'+String(el.className).slice(0,50)+' '+Math.round(r.left)+'..'+Math.round(r.right))}
 }
 for(const el of document.querySelectorAll('button,a,input,[role=button],select')){const r=el.getBoundingClientRect(); const cs=getComputedStyle(el); if(cs.display==='none'||r.width===0||cs.opacity==='0')continue; if(r.right<0||r.left>W)continue; if(r.width<44||r.height<44){if(out.small.length<8)out.small.push((el.tagName+':'+(el.innerText||el.getAttribute('aria-label')||el.className.toString().slice(0,20)).trim().slice(0,18)+' '+Math.round(r.width)+'x'+Math.round(r.height)))} if(el.tagName==='INPUT'&&parseFloat(cs.fontSize)<16)out.smallInputs.push(el.type+' '+cs.fontSize)}
 return out}"""
res=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for vn,w,h in VPS:
        ctx=b.new_context(viewport={"width":w,"height":h}, has_touch=w<1024, is_mobile=w<768, service_workers="block")
        pg=ctx.new_page(); errs=[]
        pg.on("console", lambda m: errs.append(m.text[:100]) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR "+str(e)[:100]))
        pg.goto(B+"/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(600)
        # make the player level 2 so more states exist, harmless
        for pageid in PAGES:
            errs.clear(); state="ok"
            try:
                if pageid.startswith("/"):
                    pg.goto(B+pageid); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1200)
                elif pageid=="classic-game":
                    pg.goto(B+"/classic"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1200)
                    pg.get_by_text("1-10").first.click(timeout=4000); pg.wait_for_timeout(700)
                    pg.get_by_text("GO !").click(timeout=4000); pg.wait_for_timeout(1200)
                elif pageid=="discovery-game":
                    pg.goto(B+"/discovery"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
                    pg.get_by_text("JOUER").click(timeout=4000); pg.wait_for_timeout(1200)
                elif pageid=="settings":
                    pg.goto(B+"/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
                    for _ in range(4): pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(200)
                    pg.keyboard.press("Enter"); pg.wait_for_timeout(900)
            except Exception as e:
                state="STATE-FAIL "+str(e).splitlines()[0][:80]
            a=pg.evaluate(JS_AUDIT)
            name=pageid.strip("/").replace("/","") or "home"
            pg.screenshot(path=f"{OUT}/{name}-{vn}.png")
            a.update(page=pageid,vp=vn,state=state,errors=list(set(errs)),hscroll=a["scrollW"]>a["W"])
            res.append(a)
            print(vn.ljust(18),pageid.ljust(15),"HSCROLL" if a["hscroll"] else "ok     ", "off=%d"%len(a["off"]), "small=%d"%len(a["small"]), "err=%d"%len(a["errors"]), state if state!="ok" else "", flush=True)
        ctx.close()
    b.close()
json.dump(res,open(f"{OUT}/matrix-{TAG}.json","w"),indent=1)
