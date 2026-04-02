class Lehmer():
    def __init__(self, m: int, a: int, seed: int):
        if m <= 0:
            raise ValueError("m must be > 0")
        if not (0 < a < m):
            raise ValueError("a must satisfy 0 < a < m")
        if not (0 <= seed < m):
            raise ValueError("seed must satisfy 0 <= seed < m")
        self.m = m
        self.a = a
        self.state = seed

    def next_int(self) -> int:
        self.state = (self.a * self.state) % self.m
        return self.state
