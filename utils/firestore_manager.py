import logging

logger = logging.getLogger(__name__)

_firebase_initialized = False


def reset_firebase_app():
    global _firebase_initialized
    try:
        import firebase_admin
        app = firebase_admin.get_app()
        firebase_admin.delete_app(app)
    except Exception:
        pass
    _firebase_initialized = False


def get_firebase_app():
    global _firebase_initialized
    import firebase_admin
    from firebase_admin import credentials
    from utils.credentials_store import get_firebase_credentials
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass
    cred_dict = get_firebase_credentials()
    cred = credentials.Certificate(cred_dict)
    app = firebase_admin.initialize_app(cred)
    _firebase_initialized = True
    return app


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
