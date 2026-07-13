from __future__ import annotations

from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException

app = FastAPI(title="TSFM Realworld Bench example endpoint")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def forecast_one(
    history: list[float], horizon: int, quantiles: list[float]
) -> dict[str, Any]:
    values = np.asarray(history, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        values = np.zeros(1, dtype=np.float64)

    last_value = float(values[-1])
    scale = float(np.nanstd(values[-min(values.size, 32):]))
    if not np.isfinite(scale) or scale <= 0:
        scale = 1e-6

    mean = np.full(horizon, last_value, dtype=np.float64)
    q_map = {}
    for level in quantiles:
        # Simple symmetric interval for demonstration only.
        offset = (float(level) - 0.5) * 2.0 * scale
        q_map[f"{level:g}"] = (mean + offset).tolist()
    return {"mean": mean.tolist(), "quantiles": q_map}


@app.post("/forecast")
def forecast(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        params = payload["parameters"]
        horizon = int(params["prediction_length"])
        quantiles = [float(level) for level in params.get("quantiles", [])]
        outputs = [
            forecast_one(item["target"], horizon, quantiles)
            for item in payload.get("inputs", [])
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not outputs:
        raise HTTPException(status_code=400, detail="No inputs supplied")
    return {"outputs": outputs}
