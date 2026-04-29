"""Utilitaires BigQuery/GDELT (local).

Ce module fournit des fonctions réutilisables pour :
    - créer un client BigQuery,
    - exécuter une requête et récupérer un ``pandas.DataFrame``,
    - sauvegarder un DataFrame localement.

Les tests automatisés (connexion/extraction) vivent dans le dossier ``tests/``.

Authentification (dans l'ordre) :
    1) Variable d'environnement ``GOOGLE_APPLICATION_CREDENTIALS`` (chemin vers un JSON Service Account)
    2) Fichier ``credentials/credentials.json`` à la racine du repo
    3) Sinon, Application Default Credentials (ADC)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

BIGQUERY_SCOPE = "https://www.googleapis.com/auth/bigquery"
CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
DEFAULT_CREDENTIALS_REL_PATH = Path("credentials") / "credentials.json"


def _repo_root() -> Path:
    """Retourne le dossier racine du projet.

    Hypothèse : ce fichier est dans ``scripts/``.
    """

    return Path(__file__).resolve().parents[1]


def resolve_credentials_path(explicit_path: str | Path | None = None) -> Path | None:
    """Résout le chemin vers un fichier de credentials Service Account.

    Args:
        explicit_path: Chemin explicite vers un JSON de Service Account.

    Returns:
        Un ``Path`` existant si trouvé, sinon ``None``.
    """

    if explicit_path is not None:
        candidate = Path(explicit_path).expanduser().resolve()
        return candidate if candidate.exists() else None

    env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        candidate = Path(env_path).expanduser().resolve()
        if candidate.exists():
            return candidate

    candidate = (_repo_root() / DEFAULT_CREDENTIALS_REL_PATH).resolve()
    if candidate.exists():
        return candidate

    return None


def get_bq_client(
    *,
    credentials_path: str | Path | None = None,
    project: str | None = None,
    readonly: bool = True,
) -> bigquery.Client:
    """Crée un client BigQuery authentifié.

    Args:
        credentials_path: Chemin explicite vers un JSON Service Account.
            Si fourni mais introuvable, une ``FileNotFoundError`` est levée.
        project: Project ID GCP à utiliser (optionnel). Si absent et si un service
            account est utilisé, on tente ``credentials.project_id``.
        readonly: Si True, utilise le scope BigQuery read-only.

    Raises:
        FileNotFoundError: Si ``credentials_path`` est fourni mais inexistant.

    Returns:
        Un client BigQuery.
    """

    resolved = resolve_credentials_path(credentials_path)
    if credentials_path is not None and resolved is None:
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    if resolved is None:
        logger.info("No service account JSON found; using Application Default Credentials (ADC)")
        return bigquery.Client(project=project)

    if readonly:
        scopes = [
            BIGQUERY_SCOPE,
        ]
    else:
        scopes = [
            CLOUD_PLATFORM_SCOPE,
        ]
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(resolved),
            scopes=scopes,
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to load service account credentials from {resolved}") from exc

    effective_project = project or credentials.project_id
    logger.info("Using service account credentials from %s (project=%s)", resolved, effective_project)
    return bigquery.Client(credentials=credentials, project=effective_project)


def extract_raw_data(client: bigquery.Client, query: str) -> pd.DataFrame:
    """Exécute une requête BigQuery et retourne un DataFrame.

    Args:
        client: Client BigQuery.
        query: Requête SQL Standard.

    Returns:
        Résultat sous forme de DataFrame.
    """

    logger.info("Running query (%d chars)", len(query))
    try:
        return client.query(query).to_dataframe()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("BigQuery query failed") from exc


def load_raw_data(df: pd.DataFrame, file_path_name: str | Path) -> Path:
    """Enregistre un DataFrame pandas dans un fichier CSV.

    Args:
        df: DataFrame à enregistrer.
        file_path_name: Chemin complet du fichier CSV de destination.

    Returns:
        Le chemin résolu du fichier écrit.
    """

    out_path = Path(file_path_name).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    logger.info("DataFrame saved to %s", out_path)
    return out_path


def _smoke_test_connection() -> None:
    """Test manuel minimal (utilisé par le bloc ``__main__``).

    Les tests automatisés sont dans ``tests/``.
    """

    client = get_bq_client()
    df = extract_raw_data(client, "SELECT 1 AS ok")
    logger.info("Connexion OK (ok=%s)", int(df.loc[0, "ok"]))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    _smoke_test_connection()
