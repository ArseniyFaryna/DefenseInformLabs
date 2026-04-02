from __future__ import annotations

import io
from pathlib import Path

from app.services.lab2.hash_service import (
    md5_text_hex,
    md5_stream_hex,
    md5_file_hex,
    save_hash_to_file,
    read_hash_from_file,
    verify_file_by_md5_file,
)


def test_md5_text_hex_empty():
    assert md5_text_hex("") == "D41D8CD98F00B204E9800998ECF8427E"


def test_md5_text_hex_abc():
    assert md5_text_hex("abc") == "900150983CD24FB0D6963F7D28E17F72"


def test_md5_text_hex_unicode_utf8():
    h1 = md5_text_hex("Привіт")
    h2 = md5_text_hex("Привіт")
    assert h1 == h2
    assert len(h1) == 32


def test_md5_stream_hex_matches_expected_for_abc():
    stream = io.BytesIO(b"abc")
    assert md5_stream_hex(stream, chunk_size=1) == "900150983CD24FB0D6963F7D28E17F72"


def test_md5_stream_hex_large_incremental_equals_single():
    data = b"abc" * 50000  # ~150KB
    s1 = io.BytesIO(data)
    h_small = md5_stream_hex(s1, chunk_size=7)

    s2 = io.BytesIO(data)
    h_big = md5_stream_hex(s2, chunk_size=1024 * 1024)

    assert h_small == h_big
    assert len(h_small) == 32


def test_md5_file_hex(tmp_path: Path):
    p = tmp_path / "x.txt"
    p.write_bytes(b"abc")
    assert md5_file_hex(p) == "900150983CD24FB0D6963F7D28E17F72"


def test_save_hash_to_file_and_read_hash_from_file(tmp_path: Path):
    md5_path = tmp_path / "a" / "b" / "hash.md5"
    save_hash_to_file("900150983cd24fb0d6963f7d28e17f72", md5_path)

    assert md5_path.exists()

    got = read_hash_from_file(md5_path)
    assert got == "900150983CD24FB0D6963F7D28E17F72"

    raw = md5_path.read_text(encoding="utf-8")
    assert raw.endswith("\n")


def test_read_hash_from_file_with_filename_format(tmp_path: Path):
    md5_path = tmp_path / "x.md5"
    md5_path.write_text(
        "900150983cd24fb0d6963f7d28e17f72  somefile.bin\n",
        encoding="utf-8",
    )
    assert read_hash_from_file(md5_path) == "900150983CD24FB0D6963F7D28E17F72"


def test_verify_file_by_md5_file_ok(tmp_path: Path):
    file_path = tmp_path / "x.txt"
    file_path.write_bytes(b"abc")

    md5_path = tmp_path / "x.md5"
    md5_path.write_text("900150983CD24FB0D6963F7D28E17F72\n", encoding="utf-8")

    res = verify_file_by_md5_file(file_path, md5_path)
    assert res.ok is True
    assert res.expected == "900150983CD24FB0D6963F7D28E17F72"
    assert res.actual == "900150983CD24FB0D6963F7D28E17F72"


def test_verify_file_by_md5_file_fail(tmp_path: Path):
    file_path = tmp_path / "x.txt"
    file_path.write_bytes(b"abc")

    md5_path = tmp_path / "x.md5"
    md5_path.write_text("D41D8CD98F00B204E9800998ECF8427E\n", encoding="utf-8")  # hash від ""

    res = verify_file_by_md5_file(file_path, md5_path)
    assert res.ok is False
    assert res.expected == "D41D8CD98F00B204E9800998ECF8427E"
    assert res.actual == "900150983CD24FB0D6963F7D28E17F72"