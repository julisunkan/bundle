"""
sync_manager.py — Stub. Firebase is now the sole database; no sync needed.
"""


def firebase_available():
    return True


def push_record(collection, record_dict):
    pass


def delete_record(collection, doc_id):
    pass


def push_setting(key, value):
    pass


def full_push_to_firebase(app=None):
    pass


def restore_from_firebase(app=None):
    pass
