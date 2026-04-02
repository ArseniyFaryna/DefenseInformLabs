from app.domain.lab1.linear_compare_algo import LinearCompareAlgo


def test_next_int_basic_known_sequence():
    # m=9, a=2, c=0, seed=1
    # x1 = (2*1) % 9 = 2
    # x2 = (2*2) % 9 = 4
    # x3 = (2*4) % 9 = 8
    # x4 = (2*8) % 9 = 7
    gen = LinearCompareAlgo(m=9, a=2, c=0, seed=1)
    out = [gen.next_int() for _ in range(4)]
    assert out == [2, 4, 8, 7]


def test_generate_matches_repeated_next_int():
    gen1 = LinearCompareAlgo(m=97, a=17, c=43, seed=5)
    gen2 = LinearCompareAlgo(m=97, a=17, c=43, seed=5)

    seq = gen1.generate(20)
    seq2 = [gen2.next_int() for _ in range(20)]
    assert seq == seq2


def test_seed_not_eaten_in_constructor_first_output_is_x1():
    m, a, c, x0 = 11, 3, 0, 7
    gen = LinearCompareAlgo(m=m, a=a, c=c, seed=x0)

    x1_expected = (a * x0 + c) % m
    assert gen.next_int() == x1_expected
