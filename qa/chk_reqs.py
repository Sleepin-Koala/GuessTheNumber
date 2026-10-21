from playwright.sync_api import sync_playwright
from lib import *; from play import *
with Servers() as srv, sync_playwright() as p:
    b = p.chromium.launch(); pl = Player(b, "r", viewport=(390, 844), touch=True); pl.go("/"); set_level(pl.pid, 3)
    reqs = []; pl.page.on("request", lambda r: reqs.append(r.method + " " + r.url.replace(API, "")) if r.url.startswith(API) else None)
    pl.go("/classic"); print("classic menu:", reqs); reqs.clear()
    pl.page.get_by_text("1-30").first.click(); pl.page.wait_for_timeout(600); print("pick level:", reqs); reqs.clear()
    pl.page.get_by_text("GO !").click(); pl.page.wait_for_timeout(1500); print("start:", reqs); reqs.clear()
    sid, n = last_session("solo"); guess_ui(pl, 2 if n != 2 else 3, 500); print("guess:", reqs); reqs.clear()
    guess_ui(pl, n, 500); pl.page.wait_for_timeout(2500); print("win:", reqs)
    b.close()
