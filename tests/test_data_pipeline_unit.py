from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock


class TestDataPipelineUnit(unittest.TestCase):
    def test_resolve_credentials_path_prefers_explicit(self) -> None:
        from scripts import data_pipeline

        with mock.patch.object(data_pipeline, "_repo_root") as repo_root_mock:
            repo_root_mock.return_value = Path("C:/tmp/does-not-matter")

            with mock.patch.object(Path, "exists", return_value=True):
                resolved = data_pipeline.resolve_credentials_path("C:/x/creds.json")

        self.assertIsNotNone(resolved)

    def test_get_bq_client_raises_when_explicit_missing(self) -> None:
        from scripts import data_pipeline

        with mock.patch.object(data_pipeline, "resolve_credentials_path", return_value=None):
            with self.assertRaises(FileNotFoundError):
                data_pipeline.get_bq_client(credentials_path="C:/missing.json")

    def test_get_bq_client_uses_adc_when_no_file(self) -> None:
        from scripts import data_pipeline

        with mock.patch.object(data_pipeline, "resolve_credentials_path", return_value=None):
            with mock.patch.object(data_pipeline.bigquery, "Client") as client_ctor:
                data_pipeline.get_bq_client(project="my-project")

        client_ctor.assert_called_once()
        _, kwargs = client_ctor.call_args
        self.assertEqual(kwargs.get("project"), "my-project")


if __name__ == "__main__":
    unittest.main()
