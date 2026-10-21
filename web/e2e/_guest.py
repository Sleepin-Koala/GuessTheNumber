"""Les tests automatises jouent en invite: sans ce reglage, un navigateur vierge affiche l'ecran d'inscription."""
from playwright.sync_api import Browser

_orig = Browser.new_context


def _new_context(self, *a, **k):
    ctx = _orig(self, *a, **k)
    ctx.add_init_script("if (!localStorage.getItem('id')) localStorage.setItem('gtn:auto-guest', '1')")
    return ctx


Browser.new_context = _new_context
