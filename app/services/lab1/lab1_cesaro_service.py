import math
import random
from dataclasses import dataclass
from app.domain.lab1.gcd import gcd
from app.domain.lab1.linear_compare_algo import LinearCompareAlgo

@dataclass
class CesaroResult:
    source: str
    pairs: int
    coprime: int
    probability: float
    pi_est: float
    abs_error: float
    rel_error: float


class Lab1CesaroService:
    @staticmethod
    def _run_cesaro(next_int_fn, pairs: int, source: str) -> CesaroResult:
        coprime = 0

        for _ in range(pairs):
            x = next_int_fn()
            y = next_int_fn()
            if gcd(x, y) == 1:
                coprime += 1

        p = coprime / pairs if pairs else 0.0

        if p <= 0.0:
            return CesaroResult(
                source=source,
                pairs=pairs,
                coprime=coprime,
                probability=p,
                pi_est=float("nan"),
                abs_error=float("nan"),
                rel_error=float("nan"),
            )

        pi_est = math.sqrt(6.0 / p)
        abs_error = abs(pi_est - math.pi)
        rel_error = abs_error / math.pi

        return CesaroResult(
            source=source,
            pairs=pairs,
            coprime=coprime,
            probability=p,
            pi_est=pi_est,
            abs_error=abs_error,
            rel_error=rel_error,
        )

    @staticmethod
    def test_lehmer(m: int, a: int, c: int, x0: int, pairs: int) -> CesaroResult:
        gen = LinearCompareAlgo(m=m, a=a, c=c, seed=x0)
        return Lab1CesaroService._run_cesaro(gen.next_int, pairs, source="Lehmer")

    @staticmethod
    def test_system(m: int, pairs: int) -> CesaroResult:
        rng = random.Random()

        def next_int():
            return rng.randrange(0, m)

        return Lab1CesaroService._run_cesaro(next_int, pairs, source="System PRNG")
