"""Gestes de jeu reutilisables (via l'interface, comme un vrai joueur)."""
from lib import *

def guess_ui(pl, n, wait=450):
    inp = pl.page.locator("input[type=number]").first
    if inp.evaluate("e => e.readOnly"):       # ecran tactile: on tape sur le clavier numerique de l'ecran
        clr = pl.page.get_by_role("button", name="Tout effacer")
        if clr.is_enabled(): clr.click()
        for d in str(n): pl.page.get_by_role("group", name="Clavier numérique").get_by_role("button", name=d, exact=True).click()
    else:
        inp.fill(str(n))
    pl.page.locator("button.guess-button").click()
    pl.page.wait_for_timeout(wait)

def start_discovery(pl, rng=None, tutorial=False):
    pl.go("/discovery")
    if rng is not None:   # le curseur n'accepte que 1, 11, 21... (pas de 10)
        pl.page.evaluate("""v => { const el = document.querySelector('input[type=range]'); const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; set.call(el, String(v)); el.dispatchEvent(new Event('input', { bubbles: true })) }""", rng)
    pl.page.get_by_text("JOUER").click(); pl.page.wait_for_timeout(1300)

def start_classic(pl, level=1, bonuses=()):
    pl.go("/classic")
    pl.page.get_by_text(f"1-{level*10}").first.click(); pl.page.wait_for_timeout(700)
    for b in bonuses: pl.page.get_by_role("button", name=b).click()
    pl.page.get_by_text("GO !").click(); pl.page.wait_for_timeout(1500)

def others(n, lo, hi, k):
    """k valeurs differentes de n dans [lo, hi]."""
    return [v for v in range(lo, hi + 1) if v != n][:k]

def set_level(pid, level):  # preparation d'un etat de depart (pas une action de joueur)
    sql("update player set level=? where id=?", level, pid, write=True)

def set_coins(pid, coins):
    sql("update player set coins=? where id=?", coins, pid, write=True)

def session_status(sid): return sql("select status from sessions where id=?", sid)[0][0]
