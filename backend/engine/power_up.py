from math import isqrt


def pair_impair(nb_o):
    return "pair" if nb_o % 2 == 0 else "impair"


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, isqrt(n) + 1):
        if n % d == 0:
            return False
    return True


def nb_premier(nb_o):
    return "premier" if is_prime(nb_o) else "pas premier"


def nb_narcissique(nb_o):
    digits = [int(e) for e in str(nb_o)]
    return "narcissique" if sum(d ** len(digits) for d in digits) == nb_o else "pas narcissique"


def is_perfect(n: int) -> bool:
    """Parfait = egal a la somme de ses diviseurs propres (6, 28, 496...)."""
    if n < 2:
        return False
    total = 1
    for d in range(2, isqrt(n) + 1):
        if n % d == 0:
            total += d
            if d != n // d:
                total += n // d
    return total == n


def nb_parfait(nb_o):
    return "parfait" if is_perfect(nb_o) else "pas parfait"
