import os
import time
from app.domain.lab1.linear_compare_algo import LinearCompareAlgo


class Lab1Service:
    @staticmethod
    def generate_seq(m: int, a: int, c: int, x0: int, n: int) -> tuple[list[int], float]:
        gen = LinearCompareAlgo(m=m, a=a, c=c, seed=x0)
        t0 = time.time()
        seq = gen.generate(n)
        return seq, time.time() - t0

    @staticmethod
    def period_until_seed(m: int, a: int, c: int, x0: int, max_steps: int = 5_000_000) -> int | None:
        def f(x: int) -> int:
            return (a * x + c) % m

        x1 = f(x0)
        x = x1
        for k in range(1, max_steps + 1):
            x = f(x)
            if x == x1:
                return k
        return None

    @staticmethod
    def save_to_file(numbers: list[int], filename: str = "lab1.txt") -> str:
        with open(filename, "w", encoding="utf-8") as f:
            for num in numbers:
                f.write(f"{num}\n")
        return os.path.abspath(filename)
