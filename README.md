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

Create a public Hugging Face **Docker Space**, then copy the endpoint template:

```bash
export SPACE_ID="your-hf-username/your-forecast-space"
git clone "https://huggingface.co/spaces/${SPACE_ID}" forecast-space
cp examples/community_endpoint/{app.py,Dockerfile,requirements.txt,README.md,.dockerignore} forecast-space/
```

Replace `forecast_one` in `forecast-space/app.py`, commit, and push that Space.
When its `/health` route is ready, validate the deployed `/forecast` route:

```bash
python scripts/validate_external_model_endpoint.py \
  --endpoint-url "https://your-hf-username-your-forecast-space.hf.space/forecast" \
  --model-id "your-hf-username/your-model"
```

A successful check prints `"status": "ok"`. Copy
`configs/models/community_external_example.yaml`, fill in the public model card
and Space URLs, and submit it in a leaderboard request.

See [the complete protocol](docs/community_model_submission.md) and
[`paper/getting_started.tex`](paper/getting_started.tex) for the full workflow.
