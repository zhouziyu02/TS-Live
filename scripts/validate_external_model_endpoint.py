#!/usr/bin/env python3
"""Validate a TS-Live community forecast endpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from urllib.parse import urlparse

import httpx


QUANTILES = [0.1, 0.5, 0.9]
MAX_RESPONSE_BYTES = 5 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--prediction-length", type=int, default=8)
    parser.add_argument("--context-length", type=int, default=64)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--wait-seconds", type=float, default=0.0)
    parser.add_argument("--retry-interval", type=float, default=15.0)
    parser.add_argument("--allow-http", action="store_true")
    return parser.parse_args()


def validate_url(url: str, allow_http: bool) -> None:
    parsed = urlparse(url)
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("endpoint must be an absolute http(s) URL")
    if parsed.scheme != "https" and not (allow_http and local):
        raise ValueError("public endpoints must use HTTPS")


def vector(values: object, length: int, label: str) -> list[float]:
    if not isinstance(values, list) or len(values) < length:
        raise ValueError(f"{label} must contain at least {length} values")
    parsed = [float(value) for value in values[:length]]
    if not all(math.isfinite(value) for value in parsed):
        raise ValueError(f"{label} contains non-finite values")
    return parsed


def validate_response(data: object, length: int) -> dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError("response must be a JSON object")
    outputs = data.get("outputs") or data.get("forecasts")
    if not isinstance(outputs, list) or not outputs or not isinstance(outputs[0], dict):
        raise ValueError("response must include a non-empty outputs list")
    output = outputs[0]
    quantiles = output.get("quantiles")
    if not isinstance(quantiles, dict):
        raise ValueError("first output must include a quantiles object")
    mean = vector(output.get("mean", quantiles.get("0.5")), length, "mean")
    for level in QUANTILES:
        key = f"{level:g}"
        vector(quantiles.get(key), length, f"quantile {key}")
    return {"mean": mean, "quantile_keys": sorted(quantiles)}


def main() -> int:
    args = parse_args()
    validate_url(args.endpoint_url, args.allow_http)
    context = [math.sin(index / 6.0) + index * 0.01 for index in range(args.context_length)]
    opaque_id = hashlib.sha256(b"validation_series:0").hexdigest()[:16]
    payload = {
        "protocol_version": "tsfm-realworld-v1",
        "model": args.model_id,
        "inputs": [{"series_id": f"series-{opaque_id}", "target": context}],
        "parameters": {
            "prediction_length": args.prediction_length,
            "freq": "h",
            "quantiles": QUANTILES,
        },
    }
    deadline = time.monotonic() + max(0.0, args.wait_seconds)
    with httpx.Client(timeout=args.timeout, trust_env=False) as client:
        while True:
            try:
                response = client.post(args.endpoint_url, json=payload)
                response.raise_for_status()
                if len(response.content) > MAX_RESPONSE_BYTES:
                    raise ValueError("endpoint response exceeds 5 MiB")
                checked = validate_response(response.json(), args.prediction_length)
                break
            except (ValueError, httpx.HTTPError, json.JSONDecodeError) as exc:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise
                delay = min(max(0.1, args.retry_interval), remaining)
                print(
                    f"Endpoint not ready ({exc}); retrying in {delay:.1f}s",
                    file=sys.stderr,
                )
                time.sleep(delay)
    print(json.dumps({
        "status": "ok",
        "model_id": args.model_id,
        "prediction_length": args.prediction_length,
        "forecast_keys": ["mean", *[f"{level:g}" for level in QUANTILES]],
        "mean_preview": checked["mean"][:3],
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, httpx.HTTPError, json.JSONDecodeError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
