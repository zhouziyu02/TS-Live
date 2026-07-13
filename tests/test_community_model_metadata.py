from __future__ import annotations

import unittest

from scripts.generate_community_model_metadata import build_metadata


class CommunityModelMetadataTest(unittest.TestCase):
    def test_builds_safe_top_level_models_schema(self) -> None:
        metadata = build_metadata(
            model_id="hf-user/my-model",
            display_name='Model "Quoted" Name',
            space_id="hf-user/my-space",
            endpoint_url="https://hf-user-my-space.hf.space/forecast",
        )
        model = metadata["models"][0]
        self.assertFalse(model["enabled"])
        self.assertEqual(model["model_type"], "external_api")
        self.assertEqual(model["display_name"], 'Model "Quoted" Name')
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
                    space_id="hf-user/my-space",
                    endpoint_url=endpoint,
                )


if __name__ == "__main__":
    unittest.main()
