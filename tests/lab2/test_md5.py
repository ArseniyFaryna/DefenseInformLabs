from app.domain.lab2.md5 import MD5

VECTORS = [
    (b"", "D41D8CD98F00B204E9800998ECF8427E"),
    (b"a", "0CC175B9C0F1B6A831C399E269772661"),
    (b"abc", "900150983CD24FB0D6963F7D28E17F72"),
    (b"message digest", "F96B697D7CB7938D525A2F31AAF161D0"),
    (b"abcdefghijklmnopqrstuvwxyz", "C3FCD3D76192E4007DFB496CCA67E13B"),
    (b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", "D174AB98D277D9F5A5611C2C9F419D9F"),
    (
        b"12345678901234567890123456789012345678901234567890123456789012345678901234567890",
        "57EDF4A22BE3C955AC49DA2E2107B67A",
    ),
]


def test_md5_rfc_vectors():
    for msg, expected in VECTORS:
        got = MD5().update(msg).hexdigest().upper()
        assert got == expected


def test_md5_incremental_update_equals_single_update():
    data = b"abc" * 10000
    h1 = MD5().update(data).hexdigest().upper()

    h2_obj = MD5()
    for i in range(0, len(data), 123):
        h2_obj.update(data[i:i + 123])
    h2 = h2_obj.hexdigest().upper()

    assert h1 == h2