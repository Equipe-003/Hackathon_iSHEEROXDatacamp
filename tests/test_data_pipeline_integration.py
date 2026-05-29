from __future__ import annotations

import os
import unittest


def _integration_enabled() -> bool:
    return os.getenv("RUN_BIGQUERY_INTEGRATION_TESTS") == "1"


@unittest.skipUnless(_integration_enabled(), "Set RUN_BIGQUERY_INTEGRATION_TESTS=1 to run live BigQuery tests")
class TestDataPipelineIntegration(unittest.TestCase):
    def test_bigquery_connection_smoke(self) -> None:
        from scripts.data_pipeline import extract_raw_data, get_bq_client

        client = get_bq_client()
        df = extract_raw_data(client, "SELECT 1 AS ok")
        self.assertEqual(int(df.loc[0, "ok"]), 1)


if __name__ == "__main__":
    unittest.main()
