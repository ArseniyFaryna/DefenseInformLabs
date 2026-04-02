from pydantic import BaseModel, Field


class LCGParams(BaseModel):
    m: int = Field(..., gt=0)
    a: int = Field(..., ge=0)
    c: int = Field(..., ge=0)
    x0: int = Field(..., ge=0)

class Lab1Request(BaseModel):
    params: LCGParams
    count: int = Field(..., gt=0)
    show: int = Field(200, ge=0)
    max_steps_period: int = 10000000

class PeriodSeedRequest(BaseModel):
    params: dict
    max_steps: int = Field(5_000_000, gt=0)

class CesaroRequest(BaseModel):
    params: LCGParams
    pairs: int = Field(..., gt=0)
