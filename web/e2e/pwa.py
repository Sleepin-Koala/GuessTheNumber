import json, sys
from playwright.sync_api import sync_playwright
B="http://127.0.0.1:4173"; R={}
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page()
    errs=[]; pg.on("console", lambda m: errs.append(m.text[:120]) if m.type=="error" else None)
    pg.goto(B+"/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1500)
    R["sw_registered"]=pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!r&&!!r.active)")
    pg.reload(); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
    R["sw_controls_page"]=pg.evaluate("!!navigator.serviceWorker.controller")
    m=pg.evaluate("fetch('/manifest.webmanifest').then(r=>r.json())"); R["manifest"]={k:m.get(k) for k in ["name","short_name","start_url","scope","display","id","background_color","theme_color"]}
    R["icons"]=[(i["sizes"],i.get("purpose")) for i in m["icons"]]
    R["head_links"]=pg.evaluate("[...document.querySelectorAll('link[rel=manifest],link[rel=apple-touch-icon],meta[name=theme-color],meta[name=viewport]')].map(e=>e.outerHTML)")
    R["cache_keys"]=pg.evaluate("caches.keys()")
    # icon fetchability
    R["icon_status"]={u:pg.evaluate(f"fetch('{u}').then(r=>r.status)") for u in ["/icons/icon-192.png","/icons/icon-512.png","/icons/icon-maskable-512.png","/icons/apple-touch-icon.png","/offline.html"]}
    # offline: reload shell + SPA route
    ctx.set_offline(True)
    pg.goto(B+"/"); pg.wait_for_timeout(1500)
    R["offline_root_renders_app"]=pg.locator("body").inner_text()[:60].replace("\n"," ")
    R["offline_root_has_ui"]="GUESS THE NUMBER" in pg.locator("body").inner_text() or pg.locator("button").count()>0
    pg.goto(B+"/shop"); pg.wait_for_timeout(1500)
    R["offline_deep_route_loads_shell"]=pg.locator("#root").inner_html()!="" 
    pg.screenshot(path=sys.argv[1]+"/offline-shop-390x844.png")
    ctx.set_offline(False)
    R["console_errors"]=list(set(errs))
    b.close()
print(json.dumps(R,indent=1))
json.dump(R,open(sys.argv[1]+"/pwa.json","w"),indent=1)
