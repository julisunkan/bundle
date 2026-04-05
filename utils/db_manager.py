"""
db_manager.py — Stub. Firebase is now the sole database.
SQLite and MySQL have been removed.
"""


def get_db_uri():
    return 'sqlite:///:memory:'


def load_config():
    return {'db_type': 'firebase'}


def save_config(cfg):
    pass


def test_mysql_connection(host, port, database, user, password, use_ssl=False):
    return False, 'MySQL is not supported. Firebase is the only database.'


def export_as_sqlite():
    return b'-- Firebase is the only database; SQLite export is not available.\n'


def export_as_mysql():
    return b'-- Firebase is the only database; MySQL export is not available.\n'


def import_sql_dump(sql_text, cfg=None):
    return {'success': False, 'message': 'SQL import is not supported. Firebase is the only database.', 'errors': []}
