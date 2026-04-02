from pydantic import BaseModel
from typing import List

class TextIn(BaseModel):
    text: str


class SaveHashIn(BaseModel):
    hash_hex: str
    out_path: str

class RfcTestRow(BaseModel):
    message: str
    expected: str
    actual: str
    ok: bool

class RfcTestResponse(BaseModel):
    all_ok: bool
    passed: int
    total: int
    rows: List[RfcTestRow]