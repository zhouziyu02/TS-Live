from __future__ import annotations

import unittest

from scripts.generate_community_model_metadata import build_metadata


class CommunityModelMetadataTest(unittest.TestCase):
    def test_builds_safe_top_level_models_schema(self) -> None:
        metadata = build_metadata(
            model_id="hf-user/my-model",
            display_name='Model "Quoted" Name',
            code_url="https://github.com/hf-user/my-endpoint",
            endpoint_url="https://forecast.example.org/forecast",
        )
        model = metadata["models"][0]
        self.assertFalse(model["enabled"])
        self.assertEqual(model["model_type"], "external_api")
        self.assertEqual(model["display_name"], 'Model "Quoted" Name')
        self.assertEqual(model["code_link"], "https://github.com/hf-user/my-endpoint")
        self.assertEqual(model["max_response_bytes"], 5 * 1024 * 1024)

    def test_rejects_non_https_or_wrong_route(self) -> None:
        for endpoint in (
            "http://example.com/forecast",
            "https://example.com/predict",
        ):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                build_metadata(
                    model_id="hf-user/my-model",
                    display_name="Model",
                    code_url="https://github.com/hf-user/my-endpoint",
                    endpoint_url=endpoint,
                )

    def test_rejects_non_https_or_credentialed_code_url(self) -> None:
        for code_url in (
            "http://github.com/hf-user/my-endpoint",
            "https://token@example.com/source",
            "https://example.com/source#fragment",
        ):
            with self.subTest(code_url=code_url), self.assertRaises(ValueError):
                build_metadata(
                    model_id="hf-user/my-model",
                    display_name="Model",
                    code_url=code_url,
                    endpoint_url="https://forecast.example.org/forecast",
                )


if __name__ == "__main__":
    unittest.main()
