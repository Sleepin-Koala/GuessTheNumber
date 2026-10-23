"""In-game fit at many sizes incl. landscape: does the Classic/Discovery play screen scroll or clip?"""
from playwright.sync_api import sync_playwright
from lib import *; from play import *
JS = """() => { const bad=[]; for (const el of document.querySelectorAll('body *')) { const r=el.getBoundingClientRect(); const cs=getComputedStyle(el);
 if (cs.position==='fixed'||cs.display==='none'||r.width===0) continue; if (r.right>innerWidth+1||r.left<-1) bad.push('X '+el.tagName+'.'+el.className.toString().slice(0,40)+' '+Math.round(r.left)+'..'+Math.round(r.right)) }
 const sc=[...document.querySelectorAll('*')].filter(e=>{const c=getComputedStyle(e);return (c.overflowY==='auto'||c.overflowY==='scroll')&&e.scrollHeight>e.clientHeight+1}).map(e=>e.className.toString().slice(0,40)+' '+e.scrollHeight+'>'+e.clientHeight);
 return {docY: document.documentElement.scrollHeight-innerHeight, docX: document.documentElement.scrollWidth-innerWidth, inner: sc, off: bad.slice(0,3)} }"""
with Servers() as srv, sync_playwright() as p:
    b = p.chromium.launch()
    for vp in ((280, 653), (360, 640), (390, 844), (430, 932), (844, 390), (667, 375), (768, 1024), (1024, 768), (1280, 720)):
        pl = Player(b, f"f{vp[0]}", viewport=vp, touch=vp[0] < 900); pl.go("/"); set_level(pl.pid, 5)
        for mode in ("classic", "discovery"):
            start_classic(pl, 3) if mode == "classic" else start_discovery(pl)
            pl.page.wait_for_timeout(700)
            for t in ("OK",):
                bt = pl.page.get_by_role("button", name=t, exact=True)
                if bt.count(): bt.click()
            r = pl.page.evaluate(JS); flag = "OK " if not (r["docY"] > 0 or r["docX"] > 0 or r["inner"] or [o for o in r["off"] if "SVG" not in o]) else "BAD"
            print(flag, vp, mode, r if flag == "BAD" else ""); pl.shot(f"fit2_{mode}_{vp[0]}x{vp[1]}"); pl.go("/")
        pl.close()
    b.close()
