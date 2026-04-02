import math
from app.services.lab1.lab1_cesaro_service import Lab1CesaroService


def test_lehmer_basic_fields():
    r = Lab1CesaroService.test_lehmer(
        m=2147483647,
        a=48271,
        c=46368,
        x0=12345,
        pairs=5000,
    )

    assert r.pairs == 5000
    assert 0 <= r.coprime <= r.pairs
    assert 0.0 <= r.probability <= 1.0
    assert math.isfinite(r.pi_est)
    assert r.pi_est > 0


def test_system_basic_fields():
    r = Lab1CesaroService.test_system(m=1_000_003, pairs=5000)

    assert r.pairs == 5000
    assert 0 <= r.coprime <= r.pairs
    assert 0.0 <= r.probability <= 1.0
    assert math.isfinite(r.pi_est)
    assert r.pi_est > 0


def test_pairs_zero_returns_nans():
    r = Lab1CesaroService._run_cesaro(lambda: 1, pairs=0, source="X")

    assert r.pairs == 0
    assert r.coprime == 0
    assert r.probability == 0.0
    assert math.isnan(r.pi_est)
    assert math.isnan(r.abs_error)
    assert math.isnan(r.rel_error)


def test_controlled_probability_half():
    pairs = 100
    seq = ([1, 2] * (pairs // 2)) + ([2, 4] * (pairs // 2))
    it = iter(seq)

    r = Lab1CesaroService._run_cesaro(lambda: next(it), pairs=pairs, source="Controlled")

    assert r.coprime == pairs // 2
    assert math.isclose(r.probability, 0.5, abs_tol=1e-12)

    expected_pi = math.sqrt(12.0)  # sqrt(6 / 0.5)
    assert math.isclose(r.pi_est, expected_pi, abs_tol=1e-12)
