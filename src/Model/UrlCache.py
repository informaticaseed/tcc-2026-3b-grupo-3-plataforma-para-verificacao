import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


DEFAULT_DATABASE_PATH = Path("data") / "url_checks.db"


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    scheme = parts.scheme.lower()
    hostname = (parts.hostname or "").lower().rstrip(".")
    port = parts.port

    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{hostname}:{port}"
    else:
        host = hostname

    path = parts.path or "/"
    return urlunsplit((scheme, host, path, parts.query, ""))


class UrlResultCache:
    def __init__(self, database_path=None):
        configured_path = os.getenv("URL_CACHE_DB_PATH")
        self.database_path = Path(database_path or configured_path or DEFAULT_DATABASE_PATH)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS checked_urls (
                        normalized_url TEXT PRIMARY KEY,
                        original_url TEXT NOT NULL,
                        result TEXT NOT NULL,
                        checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

    def get(self, url: str):
        normalized_url = normalize_url(url)
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT result FROM checked_urls WHERE normalized_url = ?",
                (normalized_url,),
            ).fetchone()

        return json.loads(row["result"]) if row else None

    def set(self, url: str, result):
        normalized_url = normalize_url(url)
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                """
                INSERT INTO checked_urls (normalized_url, original_url, result, checked_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(normalized_url) DO UPDATE SET
                    original_url = excluded.original_url,
                    result = excluded.result,
                    checked_at = CURRENT_TIMESTAMP
                """,
                (normalized_url, url, json.dumps(result, ensure_ascii=False)),
            )
