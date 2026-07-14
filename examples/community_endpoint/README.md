# Minimal Community Forecast Endpoint

This is a tiny reference implementation for the external model API described in
the [TS-Live submission protocol](https://github.com/zhouziyu02/TS-Live/blob/main/docs/community_model_submission.md).

It is intentionally a naive forecaster. Replace `forecast_one` with your model
inference code and deploy it as a public HTTPS service owned by the model
submitter. The template is standard FastAPI/Docker and is not tied to a hosting
provider.

## Hosting requirement

Deploy the files on infrastructure you control and expose container port 7860
through HTTPS. The public service must provide:

- `GET /health`, which returns HTTP 200;
- `POST /forecast`, which follows the TS-Live protocol.

An institutional server, an existing cloud service, or a container platform can
host the endpoint. Hugging Face Gradio and Docker Spaces currently require a
paid plan for individuals, so a Space is optional and must not be assumed by
the submission workflow. A Static Space cannot run this Python service.

Whichever host is used, configure enough capacity for repeated evaluation and
allow for cold starts within the declared timeout and retry settings.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 7860
```

Validate:

```bash
python3 scripts/validate_external_model_endpoint.py \
  --endpoint-url http://localhost:7860/forecast \
  --model-id ExampleEndpoint \
  --allow-http
```

Successful validation prints JSON containing `"status": "ok"`. It does not
deploy the service or enable the leaderboard entry. After local validation,
deploy the same code behind HTTPS and validate the public `/forecast` URL before
submitting the generated metadata through the community model request form.
