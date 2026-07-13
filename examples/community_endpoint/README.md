---
title: TSFM Forecast Endpoint Template
emoji: 📈
colorFrom: blue
colorTo: yellow
sdk: docker
app_port: 7860
---

# Minimal Community Forecast Endpoint

This is a tiny reference implementation for the external model API described in
`docs/community_model_submission.md`.

It is intentionally a naive forecaster. Replace `forecast_one` with your model
inference code and deploy it as a **public Hugging Face Docker Space** or
another HTTPS service owned by the model submitter.

## Deploy on Hugging Face

1. Create a new Hugging Face Space and select **Docker** as the SDK.
2. Copy `app.py`, `Dockerfile`, and `requirements.txt` from this directory into
   the root of the Space repository.
3. Keep the Space public and ensure its `/health` endpoint returns HTTP 200.
4. Use `https://<owner>-<space-name>.hf.space/forecast` as `endpoint_url`.

Free Spaces can sleep. For reliable repeated evaluation, configure hardware
that remains available or use a Hugging Face Inference Endpoint.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

Validate:

```bash
python3 ../../scripts/validate_external_model_endpoint.py \
  --endpoint-url http://localhost:7860/forecast \
  --model-id ExampleEndpoint \
  --allow-http
```

Successful validation prints JSON containing `"status": "ok"`. It does not
upload the model or enable the leaderboard entry; submit the reviewed model
metadata separately as described in `docs/community_model_submission.md`.
