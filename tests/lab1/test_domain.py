import pytest
from app.domain.lab1.gcd import gcd
from app.domain.lab1.lehmer import Lehmer
from app.domain.lab1.linear_compare_algo import LinearCompareAlgo

def test_gcd_basic():
    assert gcd(54, 24) == 6

def test_gcd_same_numbers():
    assert gcd(10, 10) == 10


def test_gcd_with_zero_a():
    assert gcd(0, 5) == 5

def test_gcd_both_zero():
    assert gcd(0, 0) == 0


def test_gcd_negative_numbers():
    assert gcd(-54, 24) == 6
    assert gcd(54, -24) == 6
    assert gcd(-54, -24) == 6


def test_gcd_coprime():
    assert gcd(17, 13) == 1


def test_gcd_large_numbers():
    assert gcd(123456, 789012) == 12

def test_lehmer_next_int_basic():
    gen = Lehmer(m=9, a=2, seed=3)

    assert gen.next_int() == 6

    assert gen.next_int() == 3


def test_lehmer_state_changes():
    gen = Lehmer(m=13, a=2, seed=5)
    first = gen.next_int()
    second = gen.next_int()

    assert first != second


def test_lehmer_invalid_m():
    with pytest.raises(ValueError):
        Lehmer(m=0, a=5, seed=1)


def test_lehmer_invalid_a_or_seed():
    with pytest.raises(ValueError):
        Lehmer(m=10, a=10, seed=1)

    with pytest.raises(ValueError):
        Lehmer(m=10, a=5, seed=10)

def test_next_int_basic():
    gen = LinearCompareAlgo(m=9, a=2, c=1, seed=3)
    assert gen.next_int() == 7
    assert gen.next_int() == 6

def test_generate_sequence():
    gen = LinearCompareAlgo(m=9, a=2, c=1, seed=3)
    result = gen.generate(3)

    assert result == [7, 6, 4]

def test_generate_invalid_n():
    gen = LinearCompareAlgo(m=10, a=1, c=1, seed=1)

    with pytest.raises(ValueError):
        gen.generate(0)