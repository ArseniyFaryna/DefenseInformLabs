from app.services.lab1.lab1_service import Lab1Service


def _period_math(m: int, a: int, c: int, x0: int, limit: int = 1_000_000):
    x = x0
    for k in range(1, limit + 1):
        x = (a * x + c) % m
        if x == x0:
            return k
    return None


def test_period_until_seed_matches_math_small_case():
    m, a, c, x0 = 9, 2, 0, 1

    expected = _period_math(m, a, c, x0, limit=1000)
    got = Lab1Service.period_until_seed(m, a, c, x0, max_steps=1000)

    assert expected == got


def test_period_until_seed_returns_none_if_limit_small():
    m, a, c, x0 = 97, 17, 43, 5

    got = Lab1Service.period_until_seed(m, a, c, x0, max_steps=3)
    assert got is None
