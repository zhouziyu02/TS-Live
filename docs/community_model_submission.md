# Community Model Submission Protocol

This leaderboard supports community time-series foundation models without
running untrusted user code in the leaderboard process. Community models should
be hosted by the model owner behind a standard HTTPS forecast endpoint.

## Why Not Run Submitted Weights Directly

Loading arbitrary Hugging Face repositories inside the evaluator would make the
leaderboard responsible for:

- executing third-party code and dependencies,
- paying inference compute for every refresh,
- isolating network/file-system side effects,
- debugging model-specific runtime failures.

For a public, continuously refreshed leaderboard, the safer and more scalable
default is a self-hosted endpoint: the owner pays for inference, while the
leaderboard sends identical causal context windows and scores only returned
forecasts.

## Submission Requirements

Submit a Hugging Face model repo, a public URL for the endpoint code or service,
and a public HTTPS forecast endpoint operated by the model owner. The endpoint
may run on an institutional server, an existing cloud service, or any container
platform. Hugging Face hosting and a Hugging Face PRO subscription are not
required.

The repository includes a portable FastAPI/Docker example in
`examples/community_endpoint/`. Copy the files into a public endpoint-code
repository, replace `forecast_one`, and deploy them on infrastructure you
control. The resulting `/forecast` route must be reachable without sending
participant credentials. A paid Hugging Face Space or Inference Endpoint is an
optional host, not part of the submission protocol.

The submitted config follows `configs/models/community_external_example.yaml`:

```yaml
models:
  - model_id: hf-user/my-tsfm
    display_name: My-TSFM
    model_type: external_api
    endpoint_url: https://forecast.example.org/forecast
    model_link: https://huggingface.co/hf-user/my-tsfm
    code_link: https://github.com/example-org/my-tsfm-endpoint
    enabled: false
```

New entries stay `enabled: false` until maintainers validate the endpoint,
review model metadata, and decide when its future-only evaluation window begins.

## Request Schema

The leaderboard sends `POST endpoint_url` with JSON:

```json
{
  "protocol_version": "tsfm-realworld-v1",
  "model": "hf-user/my-tsfm",
  "inputs": [
    {
      "series_id": "series-opaquehash",
      "target": [1.0, 1.2, 1.4]
    }
  ],
  "parameters": {
    "prediction_length": 24,
    "freq": "H",
    "quantiles": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
  }
}
```

By default, raw dataset names and original item IDs are not sent. The endpoint
receives only the historical context, frequency, horizon, requested quantiles,
and an opaque series identifier.

The leaderboard never sends future targets, ground truth, private metric values,
HF tokens, or other contestants' predictions.

## Response Schema

Return a JSON object with one output per input:

```json
{
  "outputs": [
    {
      "mean": [1.5, 1.6],
      "quantiles": {
        "0.1": [1.1, 1.2],
        "0.5": [1.5, 1.6],
        "0.9": [1.9, 2.0]
      }
    }
  ]
}
```

The adapter also accepts `quantile_predictions`:

```json
{
  "outputs": [
    {
      "mean": [1.5, 1.6],
      "quantile_predictions": [
        {"level": 0.1, "values": [1.1, 1.2]},
        {"level": 0.9, "values": [1.9, 2.0]}
      ]
    }
  ]
}
```

Forecast arrays must be finite numeric values and at least
`prediction_length` long.

## Safety and Robustness Controls

The evaluator:

- requires HTTPS for non-localhost endpoints,
- never imports or executes community model code,
- sends only context windows, never labels,
- hides original item IDs unless `send_item_metadata: true` is explicitly set,
- enforces request timeout, retry count, max context length, and max response size,
- rejects non-finite forecasts, missing outputs, and short forecasts,
- records only metric rows in `evaluation_metrics.jsonl`.

Endpoint owners are responsible for their own rate limits, uptime, hardware,
dependencies, and inference cost.

## Validation

Install the repository requirements, copy the endpoint template, and replace
`forecast_one` with the model inference code:

```bash
python -m pip install -r requirements.txt
mkdir -p forecast-service
cp examples/community_endpoint/app.py forecast-service/
cp examples/community_endpoint/Dockerfile forecast-service/
cp examples/community_endpoint/requirements.txt forecast-service/
cp examples/community_endpoint/.dockerignore forecast-service/
```

Run and validate it locally before deployment:

```bash
python -m pip install -r forecast-service/requirements.txt
python -m uvicorn app:app --app-dir forecast-service \
  --host 127.0.0.1 --port 7860
```

In another terminal:

```bash
python scripts/validate_external_model_endpoint.py \
  --endpoint-url http://127.0.0.1:7860/forecast \
  --model-id hf-user/my-tsfm \
  --allow-http
```

Deploy `forecast-service/` using the HTTPS-capable provider or server you
control. Before review, run the validator against the public URL with a wait
window that covers a possible cold start:

```bash
python3 scripts/validate_external_model_endpoint.py \
  --endpoint-url https://forecast.example.org/forecast \
  --model-id hf-user/my-tsfm \
  --wait-seconds 900
```

The command succeeds only after it receives and validates a complete forecast;
`{"status": "ok"}` in its output is the local validation receipt. It does not
automatically submit or enable the model.

Maintainers should also run this validation before enabling an entry.

Generate the submission metadata without assuming a hosting provider:

```bash
python scripts/generate_community_model_metadata.py \
  --model-id hf-user/my-tsfm \
  --display-name My-TSFM \
  --code-url https://github.com/example-org/my-tsfm-endpoint \
  --endpoint-url https://forecast.example.org/forecast \
  --output community_model.yaml
```

Submit the public model card URL, endpoint code or service URL, forecast
endpoint URL, and the contents of `community_model.yaml` using the
[community model request form](https://github.com/zhouziyu02/TS-Live/issues/new?template=community-model.yml).

## Fairness Policy

Community models are evaluated only on releases after their accepted start time.
The leaderboard uses the same live tasks, horizons, context windows, metric
calculation, and aggregation rules as built-in models.

Because real-world data sources can be public, no live leaderboard can fully
prevent a malicious endpoint from scraping future values elsewhere. Mitigations
are:

- future-only evaluation after acceptance,
- rotating live sources and timestamps,
- no ground truth or metric feedback in endpoint requests,
- endpoint logs never receiving raw dataset names by default,
- periodic audit of suspiciously perfect or non-causal results.
