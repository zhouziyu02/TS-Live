# TS-Live Community Endpoint Starter Kit

This temporary public repository contains the files needed to connect a
self-hosted time-series foundation model to the TSFM Realworld live
leaderboard. The benchmark never downloads participant weights or executes
participant-submitted inference code. Each participant hosts a public forecast
endpoint and submits its metadata for review.

## Quick start

```bash
git clone https://github.com/zhouziyu02/TS-Live.git
cd TS-Live
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set the public identifiers and copy the portable endpoint template:

```bash
export MODEL_ID="your-hf-username/your-model"
export DISPLAY_NAME="YourModelName"
export CODE_URL="https://github.com/your-org/your-endpoint"
export ENDPOINT_URL="https://forecast.example.org/forecast"
mkdir -p forecast-service
cp examples/community_endpoint/app.py forecast-service/
cp examples/community_endpoint/Dockerfile forecast-service/
cp examples/community_endpoint/requirements.txt forecast-service/
cp examples/community_endpoint/.dockerignore forecast-service/
```

Replace `forecast_one` in `forecast-service/app.py`, add its model dependencies,
and test it locally:

```bash
python -m pip install -r forecast-service/requirements.txt
python -m uvicorn app:app --app-dir forecast-service \
  --host 127.0.0.1 --port 7860
```

In another terminal, validate the local protocol:

```bash
python scripts/validate_external_model_endpoint.py \
  --endpoint-url http://127.0.0.1:7860/forecast \
  --model-id "${MODEL_ID}" \
  --allow-http
```

Deploy `forecast-service/` on any HTTPS-capable server or container platform
you control, then set `CODE_URL` and `ENDPOINT_URL` to the public URLs. Hugging
Face hosting is optional: current Gradio and Docker Spaces require a paid plan
for individuals, and a Static Space cannot execute this Python service.

Validate the deployed `/forecast` route. The wait window covers a possible cold
start:

```bash
python scripts/validate_external_model_endpoint.py \
  --endpoint-url "${ENDPOINT_URL}" \
  --model-id "${MODEL_ID}" \
  --wait-seconds 900
```

A successful check prints `"status": "ok"`. Generate schema-checked metadata
without hand-editing YAML:

```bash
python scripts/generate_community_model_metadata.py \
  --model-id "${MODEL_ID}" \
  --display-name "${DISPLAY_NAME}" \
  --code-url "${CODE_URL}" \
  --endpoint-url "${ENDPOINT_URL}" \
  --output community_model.yaml
```

Submit the generated file and validator receipt using the
[community model request form](https://github.com/zhouziyu02/TS-Live/issues/new?template=community-model.yml).

See [the complete protocol](docs/community_model_submission.md) for the full
workflow.
