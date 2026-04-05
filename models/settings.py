"""
settings.py — Firestore-backed key/value settings store.

Maintains the same API as the original SQLAlchemy model:
  Setting.get(key, default)
  Setting.set(key, value)
  Setting.query.all()
  Setting.query.order_by(...).all()
  Setting.query.filter_by(key=k).first()
"""
import logging

logger = logging.getLogger(__name__)

_cache = {}


class _SettingRow:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def to_dict(self):
        return {'key': self.key, 'value': self.value}


class _FakeQuery:
    def __init__(self, filters=None):
        self._filters = filters or {}

    def filter_by(self, **kwargs):
        return _FakeQuery({**self._filters, **kwargs})

    def order_by(self, *args):
        return self

    def all(self):
        try:
            from utils.firestore_manager import get_firestore_client
            docs = get_firestore_client().collection('settings').stream()
            rows = []
            for doc in docs:
                d = doc.to_dict()
                if not d:
                    continue
                key = d.get('key') or doc.id
                value = d.get('value', '')
                if self._filters:
                    match = all(str(d.get(k, '')) == str(v) for k, v in self._filters.items())
                    if not match:
                        continue
                rows.append(_SettingRow(key, value))
            rows.sort(key=lambda r: r.key)
            return rows
        except Exception as e:
            logger.error('Setting.query.all() failed: %s', e)
            return []

    def first(self):
        rows = self.all()
        return rows[0] if rows else None

    def count(self):
        return len(self.all())


class _QueryDescriptor:
    def __get__(self, obj, objtype=None):
        return _FakeQuery()


class Setting:
    query = _QueryDescriptor()

    @classmethod
    def _col(cls):
        from utils.firestore_manager import get_firestore_client
        return get_firestore_client().collection('settings')

    @classmethod
    def get(cls, key, default=None):
        if key in _cache:
            return _cache[key]
        try:
            doc = cls._col().document(key).get()
            if doc.exists:
                val = (doc.to_dict() or {}).get('value')
                _cache[key] = val
                return val
        except Exception as e:
            logger.error('Setting.get(%s) failed: %s', key, e)
        return default

    @classmethod
    def set(cls, key, value):
        _cache[key] = value
        try:
            cls._col().document(key).set({'key': key, 'value': value or ''})
        except Exception as e:
            logger.error('Setting.set(%s) failed: %s', key, e)

    @classmethod
    def invalidate_cache(cls, key=None):
        if key:
            _cache.pop(key, None)
        else:
            _cache.clear()
