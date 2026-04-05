import logging
import threading

logger = logging.getLogger(__name__)

_firebase_app = None
_firebase_failed = False
_firebase_lock = threading.Lock()
_startup_checked = False


def _do_startup_check():
    """
    Runs once at startup in a background thread with a short timeout.
    Marks Firebase as unavailable if credentials are invalid or connection fails.
    """
    global _firebase_app, _firebase_failed, _startup_checked
    import firebase_admin
    from firebase_admin import credentials, firestore
    from utils.credentials_store import get_firebase_credentials

    result = [None]
    error = [None]

    def _init():
        try:
            try:
                app = firebase_admin.get_app()
            except ValueError:
                cred_dict = get_firebase_credentials()
                if not cred_dict:
                    raise ValueError("No Firebase credentials configured. Visit /setup to add them.")
                cred = credentials.Certificate(cred_dict)
                app = firebase_admin.initialize_app(cred)
            result[0] = app
            db = firestore.client()
            list(db.collection('_ping').limit(1).stream())
        except Exception as e:
            error[0] = e

    t = threading.Thread(target=_init, daemon=True)
    t.start()
    t.join(timeout=15)

    with _firebase_lock:
        _startup_checked = True
        if t.is_alive() or error[0] is not None:
            msg = "timed out" if t.is_alive() else str(error[0])
            logger.warning("Firebase unavailable at startup: %s. Running without database.", msg)
            _firebase_failed = True
        else:
            _firebase_app = result[0]
            logger.info("Firebase connected successfully at startup.")


def startup_check():
    """Call this once during app initialization to pre-check Firebase connectivity."""
    global _startup_checked
    with _firebase_lock:
        if _startup_checked:
            return
    _do_startup_check()


def reset_firebase_app():
    global _firebase_app, _firebase_failed, _startup_checked
    with _firebase_lock:
        try:
            import firebase_admin
            if _firebase_app:
                firebase_admin.delete_app(_firebase_app)
        except Exception:
            pass
        _firebase_app = None
        _firebase_failed = False
        _startup_checked = False


def get_firebase_app():
    global _firebase_app, _firebase_failed

    with _firebase_lock:
        if _firebase_failed:
            raise RuntimeError(
                "Firebase is unavailable. Please update your Firebase credentials in the admin panel."
            )
        if _firebase_app is not None:
            return _firebase_app

    import firebase_admin
    from firebase_admin import credentials
    from utils.credentials_store import get_firebase_credentials

    with _firebase_lock:
        try:
            app = firebase_admin.get_app()
            _firebase_app = app
            return app
        except ValueError:
            pass
        cred_dict = get_firebase_credentials()
        if not cred_dict:
            _firebase_failed = True
            raise RuntimeError("No Firebase credentials configured. Visit /setup to add them.")
        cred = credentials.Certificate(cred_dict)
        try:
            app = firebase_admin.initialize_app(cred)
            _firebase_app = app
            return app
        except Exception as e:
            _firebase_failed = True
            raise RuntimeError(f"Firebase initialization failed: {e}") from e


def get_firestore_client():
    get_firebase_app()
    from firebase_admin import firestore
    return firestore.client()


def test_connection():
    try:
        db = get_firestore_client()
        list(db.collection('_ping').limit(1).stream())
        return True, "Connected to Firestore successfully."
    except Exception as e:
        return False, str(e)


def _safe(val):
    if val is None:
        return None
    if isinstance(val, (int, float, bool, str)):
        return val
    return str(val)


def export_collection(collection_name, rows):
    db = get_firestore_client()
    col_ref = db.collection(collection_name)
    batch = db.batch()
    count = 0
    for row in rows:
        doc_id = str(row.get('id', count))
        safe_row = {k: _safe(v) for k, v in row.items()}
        batch.set(col_ref.document(doc_id), safe_row)
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
    if count > 0 and count % 400 != 0:
        batch.commit()
    return count


def import_collection(collection_name):
    db = get_firestore_client()
    docs = db.collection(collection_name).stream()
    return [doc.to_dict() for doc in docs]
