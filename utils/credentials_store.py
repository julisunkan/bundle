import json
import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'credentials.db')

_FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "resume-app-db",
    "private_key_id": "1b6a1e5e6f04db729da7b7a0462db515b1e9ccef",
    "private_key": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCelEfss7jNIsUA\n"
        "JeI+IRlbs/RpbDSeEzaRLuNoMcLs4LV45OuRgIfxnEEOeP2mdoIvtY20QrRH1iSG\n"
        "2LRp0BvYp2aUv+wc6YFn8z9FIpK510cwdXQ6CXSHbrydOOJhLuD8tExK27YuDZ34\n"
        "1O0+2GUI9nEMbMHwDNLgqSy/o1B9qCDybVD4ET2x6zv63EllZLqZpjAn2QkANybm\n"
        "VHfV4oZYAgyYbg+KQEeBZMXQzEA/VqGNa+51NH76QRRxTpNr6SPGEGlX9KtjiUV4\n"
        "xENj58ICNOQpNJ2z0TnywLckHro8/9IEDtSBf+wEHq0GDku+mpkenzQPOD6XtHnv\n"
        "Ly+CfrZZAgMBAAECggEACbN+C+25uDjwjtACfXUGaV0CroFbXbFEtRCGgm0K5PVh\n"
        "PK5ad+oCRwZdV36Q2+Jjl/oWG2k6QKvJy8MNlGySC4jAJojwL5ucWkjf/cF98ucH\n"
        "2J/S1qsV6SQd30tn0/SreGIqSakTxdD48UxLYD0aPzheVZmAqsgKDYrj7SxXQ/yQ\n"
        "q0mhabw0wTNOBcFPfG4YpE/8Kswd33zErC2g1iup01zhA8LchjSpphREVNvOp9vH\n"
        "SDWDQg+N+qpFT85IM1QOFEvK342JRjiC8JRhp7UZVI7yWnZc7bCq6OaG6psapRsU\n"
        "wR3VjT3dEZ3jBhWXERwjt0EqT8veuyWjV7GieQqplQKBgQDTUL4gk2v837hr8Nzj\n"
        "MELHSHnCFxYVnw6kcBDfxrdK1g2Dmp4AkaBgvCv3lNtQA2vm1n8QNM1yYNra5FG+\n"
        "aGeiih6OaCLska+5bdl5RZ5PAgRdg9iAjQZOX5E/eNvRPDHKC7ErUuO0B47JsGQR\n"
        "Ky9bX2vQWIkUC6EfdzrqqntuFQKBgQDAHL2XRJFtfeTFVwe7h+Vdr1kAC7siRb2Y\n"
        "ORswwk5+wilheU+iGUHXHHMXsDEDaT2FWcs0QYgriaC3DDED16OTcQvQ/FcUglXb\n"
        "eBmgTijyKykTq22Ncs1/9qO01L+EmQ/viLbiPslHVA7+O/kb1YpxtqbxKjq6zfKZ\n"
        "CePhUZQ8NQKBgC9pPj8w1Fm4GDifoe+XNGRh7m+NnnbbaP2b5y1N+HHh9MZCOpEG\n"
        "G2WY0oSJ8WrSWbNBDOEl97Jh6LiT4YNHCXl+Y7yvwKYzSang65o59HrliPUyT7EH\n"
        "8xJCfuQuyaL4TnN2jBmcT1plF7RIzyrK9aUak6X7N0Y4Fb5pkd50wZzBAoGBAIDk\n"
        "R4dv56pwZsbH51Y4jPjYJnxTYpBR/ixdVBLYqtV860qMm5MEIxpx6f4gpiHFwBLx\n"
        "9dXvia68PenR8ijDyumnVOg4BSyrbXM8FuVoyyv/LSYXQ/884QdTsO4oNv59uyVY\n"
        "smsE+QI0MYL9Ndso4CP/Ce6QCKtAdd2btxp7I1tpAoGBAMF4l82FcBYk/Bn3w0tB\n"
        "uo1muXrSRmFh9x4027yhVVmQyvZvhBcHvULxj33k1xik7KaJSF8uqjFwB524v8mK\n"
        "PyY0wwixc7JXuKoQXCypzquM0wvcB913M8fE09CvXPSDqmlfe/TkqeM+WgMSwDex\n"
        "sjWDHAFlbzXlys1GLrIyFY2L\n"
        "-----END PRIVATE KEY-----\n"
    ),
    "client_email": "firebase-adminsdk-fbsvc@resume-app-db.iam.gserviceaccount.com",
    "client_id": "113113630791953731549",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40resume-app-db.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

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


def _seed(conn):
    existing = conn.execute(
        "SELECT value FROM credentials WHERE key = ?", (_CREDENTIAL_KEY,)
    ).fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO credentials (key, value) VALUES (?, ?)",
            (_CREDENTIAL_KEY, json.dumps(_FIREBASE_CREDENTIALS))
        )
        conn.commit()
        logger.info("Firebase credentials seeded into credentials.db")


def get_firebase_credentials() -> dict:
    conn = _get_conn()
    try:
        _ensure_table(conn)
        _seed(conn)
        row = conn.execute(
            "SELECT value FROM credentials WHERE key = ?", (_CREDENTIAL_KEY,)
        ).fetchone()
        if row:
            return json.loads(row["value"])
        return _FIREBASE_CREDENTIALS
    except Exception as e:
        logger.error("credentials_store error: %s — using built-in fallback", e)
        return _FIREBASE_CREDENTIALS
    finally:
        conn.close()
