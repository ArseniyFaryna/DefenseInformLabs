from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from app.domain.lab2.md5 import MD5
DEFAULT_CHUNK_SIZE = 1024 * 1024

def md5_text_hex(text: str, encoding: str = "utf-8") -> str:
    return MD5().update(text.encode(encoding)).hexdigest().upper()

def md5_stream_hex(stream: BinaryIO, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    h = MD5()
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest().upper()

def md5_file_hex(path: str | Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    p = Path(path)
    with p.open("rb") as f:
        return md5_stream_hex(f, chunk_size=chunk_size)

def save_hash_to_file(hash_hex: str, out_path: str | Path) -> None:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(hash_hex.strip().upper() + "\n", encoding="utf-8")

def read_hash_from_file(md5_path: str | Path) -> str:
    p = Path(md5_path)
    return p.read_text(encoding="utf-8").strip().split()[0].upper()

@dataclass
class VerifyResult:
    ok: bool
    expected: str
    actual: str


def verify_file_by_md5_file(file_path: str | Path, md5_path: str | Path) -> VerifyResult:
    expected = read_hash_from_file(md5_path)
    actual = md5_file_hex(file_path)
    return VerifyResult(ok=(expected == actual), expected=expected, actual=actual)