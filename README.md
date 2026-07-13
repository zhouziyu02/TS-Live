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

Create a public Hugging Face **Docker Space** in the web UI, authenticate the
CLI, then copy the endpoint template:

```bash
export SPACE_ID="your-hf-username/your-forecast-space"
hf auth login
hf auth whoami
mkdir -p forecast-space
cp examples/community_endpoint/{app.py,Dockerfile,requirements.txt,README.md,.dockerignore} forecast-space/
```

Replace `forecast_one` in `forecast-space/app.py`, then deploy without storing a
token in the repository:

```bash
hf upload "${SPACE_ID}" forecast-space . \
  --repo-type space \
  --commit-message "Deploy TSFM forecast endpoint"
```

Validate the deployed `/forecast` route. The wait window covers the initial
Docker build and a possible cold start:

```bash
python scripts/validate_external_model_endpoint.py \
  --endpoint-url "https://your-hf-username-your-forecast-space.hf.space/forecast" \
  --model-id "your-hf-username/your-model" \
  --wait-seconds 900
```

A successful check prints `"status": "ok"`. Generate schema-checked metadata
without hand-editing YAML:

```bash
python scripts/generate_community_model_metadata.py \
  --model-id "your-hf-username/your-model" \
  --display-name "Your Model" \
  --space-id "${SPACE_ID}" \
  --endpoint-url "https://your-space-direct-url.hf.space/forecast" \
  --output community_model.yaml
```

Submit the generated file and validator receipt using the
[community model request form](https://github.com/zhouziyu02/TS-Live/issues/new?template=community-model.yml).

See [the complete protocol](docs/community_model_submission.md) and
[`paper/getting_started.tex`](paper/getting_started.tex) for the full workflow.
