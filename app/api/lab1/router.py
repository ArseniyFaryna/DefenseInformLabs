from fastapi import APIRouter, HTTPException
from app.api.lab1.schema import Lab1Request, PeriodSeedRequest, CesaroRequest
from app.services.lab1.lab1_service import Lab1Service
from app.services.lab1.lab1_cesaro_service import Lab1CesaroService
import math

router = APIRouter()


def _validate_params(m: int, a: int, c: int, x0: int) -> None:
    if m <= 0:  
        raise HTTPException(status_code=400, detail="Require: m > 0")
    if a < 0 or c < 0 or x0 < 0 or a >= m or c >= m or x0 >= m:
        raise HTTPException(status_code=400, detail="Require: 0 <= a,c,x0 < m")


@router.post("/generate")
def generate(req: Lab1Request):
    p = req.params
    _validate_params(p.m, p.a, p.c, p.x0)

    seq, t = Lab1Service.generate_seq(p.m, p.a, p.c, p.x0, req.count)
    preview = seq[: req.show]

    period_val = Lab1Service.period_until_seed(
        p.m, p.a, p.c, p.x0,
        max_steps=req.max_steps_period
    )

    return {
        "count": req.count,
        "shown": len(preview),
        "preview": preview,
        "time_seconds": t,
        "period": period_val,
        "period_status": "ok" if period_val is not None else "limit",
        "max_steps_period": req.max_steps_period,
    }


@router.post("/save")
def save(req: Lab1Request):
    p = req.params
    _validate_params(p.m, p.a, p.c, p.x0)

    seq, t = Lab1Service.generate_seq(p.m, p.a, p.c, p.x0, req.count)
    path = Lab1Service.save_to_file(seq)

    period_val = Lab1Service.period_until_seed(
        p.m, p.a, p.c, p.x0,
        max_steps=req.max_steps_period
    )

    return {
        "count": req.count,
        "file_saved_to": path,
        "time_seconds": t,
        "params": p.model_dump(),
        "period": period_val,
        "period_status": "ok" if period_val is not None else "limit",
        "max_steps_period": req.max_steps_period,
    }


@router.post("/period_seed")
def period_seed(req: PeriodSeedRequest):
    p = req.params
    m = int(p["m"]); a = int(p["a"]); c = int(p["c"]); x0 = int(p["x0"])
    _validate_params(m, a, c, x0)

    period_val = Lab1Service.period_until_seed(m, a, c, x0, req.max_steps)

    if period_val is None:
        return {
            "status": "limit",
            "period": None,
            "max_steps": req.max_steps,
            "message": "Seed (x0) не повторився в межах max_steps. Можливий дуже великий період."
        }

    return {
        "status": "ok",
        "period": period_val,
        "message": "Період = кількість кроків до повтору seed (x0)."
    }


@router.post("/cesaro")
def cesaro(req: CesaroRequest):
    p = req.params
    _validate_params(p.m, p.a, p.c, p.x0)

    if req.pairs <= 0:
        raise HTTPException(status_code=400, detail="Require: pairs > 0")

    res_lehmer = Lab1CesaroService.test_lehmer(p.m, p.a, p.c, p.x0, req.pairs)
    res_sys = Lab1CesaroService.test_system(p.m, req.pairs)

    def to_dict(r):
        def safe(v):
            if v is None or (isinstance(v, float) and not math.isfinite(v)):
                return None
            return v

        return {
            "source": r.source,
            "pairs": r.pairs,
            "coprime": r.coprime,
            "probability": safe(r.probability),
            "pi_est": safe(r.pi_est),
            "abs_error": safe(r.abs_error),
            "rel_error": safe(r.rel_error),
        }

    return {
        "results": [to_dict(res_lehmer), to_dict(res_sys)],
        "pi_table": math.pi
    }
