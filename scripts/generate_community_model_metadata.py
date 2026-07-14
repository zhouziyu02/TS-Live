#!/usr/bin/env python3
"""Generate validated YAML metadata for a TS-Live community model request."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

import yaml


HUB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")


def _hub_id(value: str, label: str) -> str:
    value = value.strip()
    if not HUB_ID.fullmatch(value):
        raise ValueError(f"{label} must have the form owner/repository")
    return value


def _endpoint_url(value: str) -> str:
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("endpoint URL must be an absolute HTTPS URL")
    if parsed.path.rstrip("/") != "/forecast":
        raise ValueError("endpoint URL path must be /forecast")
    if parsed.query or parsed.fragment:
        raise ValueError("endpoint URL must not contain a query string or fragment")
    return value


def _public_https_url(value: str, label: str) -> str:
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{label} must be an absolute HTTPS URL")
    if parsed.username or parsed.password:
        raise ValueError(f"{label} must not contain embedded credentials")
    if parsed.fragment:
        raise ValueError(f"{label} must not contain a fragment")
    return value


def build_metadata(
    *, model_id: str, display_name: str, code_url: str, endpoint_url: str
) -> dict[str, object]:
    model_id = _hub_id(model_id, "model ID")
    display_name = display_name.strip()
    if not display_name:
        raise ValueError("display name must not be empty")
    code_url = _public_https_url(code_url, "code URL")
    endpoint_url = _endpoint_url(endpoint_url)
    return {
        "models": [
            {
                "model_id": model_id,
                "display_name": display_name,
                "enabled": False,
                "model_type": "external_api",
                "model_link": f"https://huggingface.co/{model_id}",
                "code_link": code_url,
                "endpoint_url": endpoint_url,
                "timeout": 90,
                "max_retries": 2,
                "max_context_points": 4096,
                "max_response_bytes": 5 * 1024 * 1024,
                "require_https": True,
                "send_item_metadata": False,
            }
        ]
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument(
        "--code-url",
        required=True,
        help="public HTTPS URL for the endpoint source code or service",
    )
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--output", type=Path, default=Path("community_model.yaml"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metadata = build_metadata(
        model_id=args.model_id,
        display_name=args.display_name,
        code_url=args.code_url,
        endpoint_url=args.endpoint_url,
    )
    rendered = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True)
    if yaml.safe_load(rendered) != metadata:
        raise RuntimeError("generated YAML did not pass its round-trip schema check")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote validated metadata to {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        raise SystemExit(f"metadata validation failed: {exc}") from exc
