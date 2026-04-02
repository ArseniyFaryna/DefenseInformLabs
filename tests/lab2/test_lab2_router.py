from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.lab2.router import router as lab2_router


def make_client() -> TestClient:
    app = FastAPI()
    app.include_router(lab2_router, prefix="/api/lab2", tags=["lab2"])
    return TestClient(app)


def test_api_md5_text_empty():
    client = make_client()
    r = client.post("/api/lab2/md5/text", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["md5"] == "D41D8CD98F00B204E9800998ECF8427E"


def test_api_md5_text_abc():
    client = make_client()
    r = client.post("/api/lab2/md5/text", json={"text": "abc"})
    assert r.status_code == 200
    assert r.json()["md5"] == "900150983CD24FB0D6963F7D28E17F72"


def test_api_md5_file_stream():
    client = make_client()
    files = {"file": ("x.txt", b"abc", "application/octet-stream")}
    r = client.post("/api/lab2/md5/file", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["filename"] == "x.txt"
    assert body["md5"] == "900150983CD24FB0D6963F7D28E17F72"


def test_api_verify_file_ok():
    client = make_client()

    file_bytes = b"abc"
    expected = "900150983CD24FB0D6963F7D28E17F72\n"

    files = {
        "file": ("x.txt", file_bytes, "application/octet-stream"),
        "md5_file": ("x.md5", expected.encode("utf-8"), "text/plain"),
    }
    r = client.post("/api/lab2/md5/verify", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["expected"] == "900150983CD24FB0D6963F7D28E17F72"
    assert body["actual"] == "900150983CD24FB0D6963F7D28E17F72"


def test_api_verify_file_fail():
    client = make_client()

    file_bytes = b"abc"
    wrong = "D41D8CD98F00B204E9800998ECF8427E\n"

    files = {
        "file": ("x.txt", file_bytes, "application/octet-stream"),
        "md5_file": ("x.md5", wrong.encode("utf-8"), "text/plain"),
    }
    r = client.post("/api/lab2/md5/verify", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["expected"] == "D41D8CD98F00B204E9800998ECF8427E"
    assert body["actual"] == "900150983CD24FB0D6963F7D28E17F72"


def test_api_rfc_tests_endpoint_all_ok():
    client = make_client()
    r = client.get("/api/lab2/md5/rfc-tests")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 7
    assert data["passed"] == 7
    assert data["all_ok"] is True

    rows = data["rows"]
    assert rows[0]["message"] == ""
    assert rows[0]["expected"] == "D41D8CD98F00B204E9800998ECF8427E"
    assert rows[0]["ok"] is True

    assert rows[2]["message"] == "abc"
    assert rows[2]["expected"] == "900150983CD24FB0D6963F7D28E17F72"
    assert rows[2]["actual"] == "900150983CD24FB0D6963F7D28E17F72"
    assert rows[2]["ok"] is True


def test_api_save_hash_to_file(tmp_path):
    client = make_client()

    out_path = tmp_path / "out.md5"
    payload = {"hash_hex": "900150983CD24FB0D6963F7D28E17F72", "out_path": str(out_path)}

    r = client.post("/api/lab2/md5/save", json=payload)
    assert r.status_code == 200
    assert r.json()["saved_to"] == str(out_path)

    saved_text = out_path.read_text(encoding="utf-8").strip().upper()
    assert saved_text == "900150983CD24FB0D6963F7D28E17F72"