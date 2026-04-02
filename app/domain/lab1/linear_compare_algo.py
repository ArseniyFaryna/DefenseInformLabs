class LinearCompareAlgo:

    def __init__(self, m: int, a: int, c: int, seed: int):
        if m <= 0:
            raise ValueError("m must be > 0")
        if not (0 <= a < m):
            raise ValueError("a must satisfy 0 <= a < m")
        if not (0 <= c < m):
            raise ValueError("c must satisfy 0 <= c < m")
        if not (0 <= seed < m):
            raise ValueError("seed must satisfy 0 <= seed < m")

        self.m = m
        self.a = a
        self.c = c
        self.state = seed

    def next_int(self) -> int:
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def generate(self, n: int) -> list[int]:
        if n <= 0:
            raise ValueError("n must be > 0")
        return [self.next_int() for _ in range(n)]
