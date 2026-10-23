"""Lance fit_check.py (skill frontenddispose) contre un serveur jetable, en jouant en invite (sans l'ecran d'inscription)."""
import runpy, sys, os
from playwright.sync_api import Browser
from lib import *
_o = Browser.new_context
def nc(self, *a, **k):
    c = _o(self, *a, **k); c.add_init_script("if (!localStorage.getItem('id')) localStorage.setItem('gtn:auto-guest','1')"); return c
Browser.new_context = nc
build_web()
with Servers() as srv:
    sys.argv = ["fit_check.py", WEB, "--paths", sys.argv[1], "--out", sys.argv[2], "--set", "full"]
    try: runpy.run_path(os.path.expanduser("~/.claude/skills/frontenddispose/scripts/fit_check.py"), run_name="__main__")
    except SystemExit: pass
