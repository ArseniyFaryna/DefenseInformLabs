import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.lab1.router import router


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(router, prefix="/lab1")
    return TestClient(app)

def test_generate_ok(client, monkeypatch):
    def fake_generate_seq(m, a, c, x0, count):
        return ([1, 2, 3, 4, 5], 0.001)

    def fake_period_until_seed(m, a, c, x0, max_steps):
        return 42

    monkeypatch.setattr("app.api.lab1.router.Lab1Service.generate_seq", fake_generate_seq)
    monkeypatch.setattr("app.api.lab1.router.Lab1Service.period_until_seed", fake_period_until_seed)

    payload = {
        "params": {"m": 10, "a": 1, "c": 1, "x0": 1},
        "count": 5,
        "show": 3,
        "max_steps_period": 1000
    }

    r = client.post("/lab1/generate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 5
    assert data["shown"] == 3
    assert data["preview"] == [1, 2, 3]
    assert data["period"] == 42
    assert data["period_status"] == "ok"

def test_save_ok(client, monkeypatch):
    def fake_generate_seq(m, a, c, x0, count):
        return ([7, 8, 9], 0.002)

    def fake_save_to_file(seq):
        return "tmp/lab1_seq.txt"

    def fake_period_until_seed(m, a, c, x0, max_steps):
        return None

    monkeypatch.setattr("app.api.lab1.router.Lab1Service.generate_seq", fake_generate_seq)
    monkeypatch.setattr("app.api.lab1.router.Lab1Service.save_to_file", fake_save_to_file)
    monkeypatch.setattr("app.api.lab1.router.Lab1Service.period_until_seed", fake_period_until_seed)

    payload = {
        "params": {"m": 10, "a": 1, "c": 1, "x0": 1},
        "count": 3,
        "show": 3,
        "max_steps_period": 10
    }

    r = client.post("/lab1/save", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["file_saved_to"] == "tmp/lab1_seq.txt"
    assert data["period"] is None
    assert data["period_status"] == "limit"
    assert data["params"] == {"m": 10, "a": 1, "c": 1, "x0": 1}


def test_save_invalid_params_400(client):
    payload = {
        "params": {"m": 10, "a": 10, "c": 1, "x0": 1},
        "count": 3,
        "show": 3,
        "max_steps_period": 10
    }
    r = client.post("/lab1/save", json=payload)
    assert r.status_code == 400
    assert "0 <= a,c,x0 < m" in r.json()["detail"]

def test_period_seed_ok(client, monkeypatch):
    def fake_period_until_seed(m, a, c, x0, max_steps):
        return 99

    monkeypatch.setattr("app.api.lab1.router.Lab1Service.period_until_seed", fake_period_until_seed)

    payload = {
        "params": {"m": 10, "a": 1, "c": 1, "x0": 1},
        "max_steps": 1000
    }

    r = client.post("/lab1/period_seed", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["period"] == 99


def test_period_seed_limit(client, monkeypatch):
    def fake_period_until_seed(m, a, c, x0, max_steps):
        return None

    monkeypatch.setattr("app.api.lab1.router.Lab1Service.period_until_seed", fake_period_until_seed)

    payload = {
        "params": {"m": 10, "a": 1, "c": 1, "x0": 1},
        "max_steps": 5
    }

    r = client.post("/lab1/period_seed", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "limit"
    assert data["period"] is None
    assert data["max_steps"] == 5

class _DummyCesaro:
    def __init__(self, source, pairs, coprime, probability, pi_est, abs_error, rel_error):
        self.source = source
        self.pairs = pairs
        self.coprime = coprime
        self.probability = probability
        self.pi_est = pi_est
        self.abs_error = abs_error
        self.rel_error = rel_error


def test_cesaro_ok(client, monkeypatch):
    def fake_test_lehmer(m, a, c, x0, pairs):
        return _DummyCesaro("Lehmer", pairs, 100, 0.6, 3.14, 0.0016, 0.0005)

    def fake_test_system(m, pairs):
        return _DummyCesaro("System", pairs, 110, 0.61, 3.141, 0.0006, 0.0002)

    monkeypatch.setattr("app.api.lab1.router.Lab1CesaroService.test_lehmer", fake_test_lehmer)
    monkeypatch.setattr("app.api.lab1.router.Lab1CesaroService.test_system", fake_test_system)

    payload = {
        "params": {"m": 10, "a": 1, "c": 1, "x0": 1},
        "pairs": 5000
    }

    r = client.post("/lab1/cesaro", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert len(data["results"]) == 2
    assert {data["results"][0]["source"], data["results"][1]["source"]} == {"Lehmer", "System"}
    assert data["results"][0]["pairs"] == 5000


def test_cesaro_pairs_invalid_validation_error(client):
    payload = {
        "params": {"m": 10, "a": 1, "c": 1, "x0": 1},
        "pairs": 0
    }
    r = client.post("/lab1/cesaro", json=payload)
    assert r.status_code == 422


def test_generate_period_limit(client, monkeypatch):
    def fake_generate_seq(m, a, c, x0, count):
        return ([1, 2, 3], 0.001)

    def fake_period_until_seed(m, a, c, x0, max_steps):
        return None

    monkeypatch.setattr("app.api.lab1.router.Lab1Service.generate_seq", fake_generate_seq)
    monkeypatch.setattr("app.api.lab1.router.Lab1Service.period_until_seed", fake_period_until_seed)

    payload = {
        "params": {"m": 10, "a": 1, "c": 1, "x0": 1},
        "count": 3,
        "show": 3,
        "max_steps_period": 5
    }
    r = client.post("/lab1/generate", json=payload)
    assert r.status_code == 200
    assert r.json()["period_status"] == "limit"
    assert r.json()["period"] is None


def test_period_seed_invalid_m_zero(client):
    payload = {
        "params": {"m": 0, "a": 0, "c": 0, "x0": 0},
        "max_steps": 100
    }
    r = client.post("/lab1/period_seed", json=payload)
    assert r.status_code == 400
    assert "m > 0" in r.json()["detail"]


def test_period_seed_invalid_params_400(client):
    payload = {
        "params": {"m": 10, "a": 10, "c": 1, "x0": 1},
        "max_steps": 100
    }
    r = client.post("/lab1/period_seed", json=payload)
    assert r.status_code == 400
    assert "0 <= a,c,x0 < m" in r.json()["detail"]


def test_cesaro_nonfinite_values(client, monkeypatch):
    import math

    class _Lehmer:
        source = "Lehmer"
        pairs = 100
        coprime = 0
        probability = None
        pi_est = float("inf")
        abs_error = float("nan")
        rel_error = None

    class _System:
        source = "System"
        pairs = 100
        coprime = 50
        probability = 0.5
        pi_est = math.pi
        abs_error = 0.0
        rel_error = 0.0

    monkeypatch.setattr("app.api.lab1.router.Lab1CesaroService.test_lehmer", lambda *a: _Lehmer())
    monkeypatch.setattr("app.api.lab1.router.Lab1CesaroService.test_system", lambda *a: _System())

    payload = {
        "params": {"m": 10, "a": 1, "c": 1, "x0": 1},
        "pairs": 100
    }
    r = client.post("/lab1/cesaro", json=payload)
    assert r.status_code == 200
    lehmer = next(x for x in r.json()["results"] if x["source"] == "Lehmer")
    assert lehmer["probability"] is None
    assert lehmer["pi_est"] is None
    assert lehmer["abs_error"] is None