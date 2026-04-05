import json
import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'credentials.db')
_CREDENTIAL_KEY = "firebase_service_account"


def _get_conn():
    os.makedirs(os.path.dirname(os.path.abspath(_DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.commit()


def get_firebase_credentials() -> dict | None:
    """
    Returns Firebase service account credentials dict, or None if not configured.
    Priority: 1. FIREBASE_CREDENTIALS env var  2. SQLite credentials.db
    Never falls back to hardcoded credentials.
    """
    env_creds = os.environ.get('FIREBASE_CREDENTIALS', '').strip()
    if env_creds:
        try:
            creds = json.loads(env_creds)
            if creds.get('private_key') and creds.get('client_email'):
                logger.info("Using Firebase credentials from FIREBASE_CREDENTIALS env var.")
                return creds
        except Exception as e:
            logger.error("Failed to parse FIREBASE_CREDENTIALS env var: %s", e)

    conn = _get_conn()
    try:
        _ensure_table(conn)
        row = conn.execute(
            "SELECT value FROM credentials WHERE key = ?", (_CREDENTIAL_KEY,)
        ).fetchone()
        if row:
            creds = json.loads(row["value"])
            if creds.get('private_key') and creds.get('client_email'):
                return creds
    except Exception as e:
        logger.error("credentials_store read error: %s", e)
    finally:
        conn.close()

    return None


def save_firebase_credentials(creds: dict) -> bool:
    """Save Firebase service account credentials to SQLite. Returns True on success."""
    conn = _get_conn()
    try:
        _ensure_table(conn)
        conn.execute(
            "INSERT OR REPLACE INTO credentials (key, value) VALUES (?, ?)",
            (_CREDENTIAL_KEY, json.dumps(creds))
        )
        conn.commit()
        logger.info("Firebase credentials saved to credentials.db")
        return True
    except Exception as e:
        logger.error("credentials_store save error: %s", e)
        return False
    finally:
        conn.close()


def clear_firebase_credentials() -> bool:
    """Remove Firebase credentials from SQLite. Returns True on success."""
    conn = _get_conn()
    try:
        _ensure_table(conn)
        conn.execute("DELETE FROM credentials WHERE key = ?", (_CREDENTIAL_KEY,))
        conn.commit()
        logger.info("Firebase credentials cleared from credentials.db")
        return True
    except Exception as e:
        logger.error("credentials_store clear error: %s", e)
        return False
    finally:
        conn.close()


def is_firebase_configured() -> bool:
    """Returns True if valid Firebase credentials are available."""
    return get_firebase_credentials() is not None
