from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, HTTPException
from app.domain.lab2.md5 import MD5
from app.services.lab2.hash_service import save_hash_to_file

from app.api.lab2.schema import RfcTestResponse, RfcTestRow, SaveHashIn, TextIn
router = APIRouter()

@router.post("/md5/text")
def md5_for_text(payload: TextIn):
    h = MD5().update(payload.text.encode("utf-8")).hexdigest().upper()
    return {"md5": h}

@router.post("/md5/file")
async def md5_for_file(file: UploadFile = File(...)):
    h = MD5()
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        h.update(chunk)

    return {"filename": file.filename, "md5": h.hexdigest().upper()}

@router.post("/md5/save")
def save_md5(payload: SaveHashIn):
    try:
        save_hash_to_file(payload.hash_hex, payload.out_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot save hash: {e}")
    return {"saved_to": payload.out_path}

@router.post("/md5/verify")
async def verify_file(file: UploadFile = File(...), md5_file: UploadFile = File(...)):
    md5_bytes = await md5_file.read()
    try:
        expected = md5_bytes.decode("utf-8").strip().split()[0].upper()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid md5 file encoding/format")

    h = MD5()
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        h.update(chunk)
    actual = h.hexdigest().upper()

    return {"ok": expected == actual, "expected": expected, "actual": actual, "filename": file.filename}

@router.get("/md5/rfc-tests", response_model=RfcTestResponse)
def rfc_tests():
    vectors = [
        ("", "D41D8CD98F00B204E9800998ECF8427E"),
        ("a", "0CC175B9C0F1B6A831C399E269772661"),
        ("abc", "900150983CD24FB0D6963F7D28E17F72"),
        ("message digest", "F96B697D7CB7938D525A2F31AAF161D0"),
        ("abcdefghijklmnopqrstuvwxyz", "C3FCD3D76192E4007DFB496CCA67E13B"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
         "D174AB98D277D9F5A5611C2C9F419D9F"),
        ("12345678901234567890123456789012345678901234567890123456789012345678901234567890",
         "57EDF4A22BE3C955AC49DA2E2107B67A"),
    ]

    rows: list[RfcTestRow] = []
    passed = 0

    for msg, expected in vectors:
        actual = MD5().update(msg.encode("utf-8")).hexdigest().upper()
        ok = (actual == expected.upper())
        if ok:
            passed += 1
        rows.append(RfcTestRow(message=msg, expected=expected.upper(), actual=actual, ok=ok))

    total = len(rows)
    all_ok = (passed == total)
    return RfcTestResponse(all_ok=all_ok, passed=passed, total=total, rows=rows)