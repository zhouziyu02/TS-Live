from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


APP_PATH = (
    Path(__file__).resolve().parents[1] / "examples" / "community_endpoint" / "app.py"
)


def _load_app_module():
    spec = importlib.util.spec_from_file_location("community_endpoint_under_test", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


endpoint = _load_app_module()


class CommunityEndpointTemplateTest(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        self.assertEqual(endpoint.health(), {"status": "ok"})

    def test_forecast_endpoint_implements_protocol(self) -> None:
        payload = {
            "protocol_version": "tsfm-realworld-v1",
            "model": "test-user/test-model",
            "inputs": [{"series_id": "series-test", "target": [1.0, 2.0, 3.0]}],
            "parameters": {
                "prediction_length": 4,
                "freq": "h",
                "quantiles": [0.1, 0.5, 0.9],
            },
        }

        response = endpoint.forecast(payload)

        self.assertEqual(len(response["outputs"]), 1)
        output = response["outputs"][0]
        self.assertEqual(len(output["mean"]), 4)
        self.assertEqual(set(output["quantiles"]), {"0.1", "0.5", "0.9"})
        self.assertTrue(
            all(len(values) == 4 for values in output["quantiles"].values())
        )


if __name__ == "__main__":
    unittest.main()
