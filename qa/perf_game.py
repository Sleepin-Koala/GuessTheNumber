"""Fluidite: taches longues du thread principal et images perdues pendant une partie, CPU ralenti x4 (telephone moyen)."""
import json
from playwright.sync_api import sync_playwright
from lib import *; from play import *
OBS = """window.__long=[]; try{ new PerformanceObserver(l=>{for(const e of l.getEntries()) window.__long.push(Math.round(e.duration))}).observe({type:'longtask',buffered:true}) }catch(e){}
window.__frames=[]; let last=performance.now(); (function tick(t){ window.__frames.push(Math.round(t-last)); last=t; requestAnimationFrame(tick) })(last)"""
with Servers() as srv, sync_playwright() as p:
    b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
    for label, gpu in (("no-3d (like most CI/phones without GPU path)", False), ("3d forced", True)):
        pl = Player(b, "perf", viewport=(390, 844), touch=True, init_script=OBS + (";localStorage.setItem('force3d','1')" if gpu else ""))
        cdp = pl.ctx.new_cdp_session(pl.page); cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        pl.go("/"); set_level(pl.pid, 3); start_classic(pl, 3); sid, n = last_session("solo")
        pl.page.evaluate("window.__long.length=0; window.__frames.length=0")
        for v in others(n, 1, 30, 3): guess_ui(pl, v, 900)
        pl.page.wait_for_timeout(1500)
        r = pl.page.evaluate("(() => { const f=window.__frames.slice(5); const s=[...f].sort((a,b)=>a-b); return {long: window.__long, frames: f.length, p50: s[Math.floor(s.length*.5)], p95: s[Math.floor(s.length*.95)], over100: f.filter(x=>x>100).length} })()")
        print(label, json.dumps(r)); pl.close()
    b.close()
