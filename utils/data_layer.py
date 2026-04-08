"""
data_layer.py — Firebase/Firestore-only storage backend.

All reads and writes go directly to Firestore. SQLite and MySQL have been
removed. Every collection uses auto-incremented integer IDs via a _counters
document in Firestore.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_RESUME_FIELDS = {
    'label', 'original_text', 'optimized_text', 'cover_letter',
    'match_score', 'missing_keywords', 'suggestions',
}
_JOB_FIELDS = {
    'company', 'position', 'status', 'job_description', 'notes', 'applied_date',
}
_MSG_FIELDS = {'name', 'email', 'subject', 'message', 'is_read'}

_JOBPOST_FIELDS = {
    'title', 'company', 'location', 'job_type', 'salary', 'tags',
    'apply_url', 'description', 'original_description', 'status',
    'featured', 'ai_rewritten', 'source', 'external_id',
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now():
    return datetime.utcnow().isoformat()


def _next_id(collection_name):
    from utils.firestore_manager import get_firestore_client
    from google.cloud import firestore as _gfs

    db = get_firestore_client()
    counter_ref = db.collection('_counters').document(collection_name)

    @_gfs.transactional
    def _txn(transaction, ref):
        snap = ref.get(transaction=transaction)
        current = int(snap.get('value')) if snap.exists else 0
        nv = current + 1
        transaction.set(ref, {'value': nv})
        return nv

    return _txn(db.transaction(), counter_ref)


def _fs_col(collection_name):
    from utils.firestore_manager import get_firestore_client
    return get_firestore_client().collection(collection_name)


def _parse_json_field(value, default):
    """Parse a field that may be stored as a JSON string back to its native type."""
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        try:
            import json as _j
            return _j.loads(value)
        except Exception:
            pass
    return default


def _doc_to_dict(doc):
    d = doc.to_dict()
    if d is None:
        return None
    d['id'] = int(doc.id) if str(doc.id).isdigit() else doc.id
    return d


def _normalize_resume(d):
    """Ensure list fields stored as JSON strings are returned as proper lists."""
    if d is None:
        return None
    d['missing_keywords'] = _parse_json_field(d.get('missing_keywords'), [])
    d['suggestions'] = _parse_json_field(d.get('suggestions'), [])
    return d


def get_firestore_client():
    from utils.firestore_manager import get_firestore_client as _gfc
    return _gfc()


# ── RESUME ────────────────────────────────────────────────────────────────────

def resume_list():
    docs = _fs_col('resumes').stream()
    rows = [_normalize_resume(_doc_to_dict(d)) for d in docs if d.to_dict()]
    rows = [r for r in rows if r is not None]
    rows.sort(key=lambda r: r.get('created_at') or '', reverse=True)
    return rows


def resume_get(resume_id):
    doc = _fs_col('resumes').document(str(resume_id)).get()
    if not doc.exists:
        return None
    return _normalize_resume(_doc_to_dict(doc))


def resume_create(data):
    new_id = _next_id('resumes')
    now = _now()
    doc = {
        'id': new_id,
        'label': data.get('label') or 'My Resume',
        'original_text': data.get('original_text') or '',
        'optimized_text': data.get('optimized_text') or '',
        'cover_letter': data.get('cover_letter') or '',
        'match_score': float(data.get('match_score') or 0),
        'missing_keywords': data.get('missing_keywords') or '[]',
        'suggestions': data.get('suggestions') or '[]',
        'created_at': now,
        'updated_at': now,
    }
    _fs_col('resumes').document(str(new_id)).set(doc)
    return dict(doc)


def resume_update(resume_id, data):
    ref = _fs_col('resumes').document(str(resume_id))
    doc = ref.get()
    if not doc.exists:
        return None
    updates = {k: v for k, v in data.items() if k in _RESUME_FIELDS}
    updates['updated_at'] = _now()
    ref.update(updates)
    return _doc_to_dict(ref.get())


def resume_delete(resume_id):
    ref = _fs_col('resumes').document(str(resume_id))
    if not ref.get().exists:
        return False
    ref.delete()
    return True


def resume_bulk_delete(ids):
    from utils.firestore_manager import get_firestore_client as _gfc
    col = _fs_col('resumes')
    batch = _gfc().batch()
    count = 0
    for rid in ids:
        batch.delete(col.document(str(rid)))
        count += 1
    batch.commit()
    return count


def resume_count():
    return len(list(_fs_col('resumes').stream()))


# ── JOB ───────────────────────────────────────────────────────────────────────

def job_list():
    docs = _fs_col('jobs').stream()
    rows = [_doc_to_dict(d) for d in docs if d.to_dict()]
    rows.sort(key=lambda r: r.get('created_at') or '', reverse=True)
    return rows


def job_get(job_id):
    doc = _fs_col('jobs').document(str(job_id)).get()
    if not doc.exists:
        return None
    return _doc_to_dict(doc)


def job_create(data):
    new_id = _next_id('jobs')
    now = _now()
    doc = {
        'id': new_id,
        'company': data.get('company') or '',
        'position': data.get('position') or '',
        'status': data.get('status') or 'Applied',
        'job_description': data.get('job_description') or '',
        'notes': data.get('notes') or '',
        'applied_date': data.get('applied_date') or now,
        'created_at': now,
        'updated_at': now,
    }
    _fs_col('jobs').document(str(new_id)).set(doc)
    return dict(doc)


def job_update(job_id, data):
    ref = _fs_col('jobs').document(str(job_id))
    doc = ref.get()
    if not doc.exists:
        return None
    updates = {k: v for k, v in data.items() if k in _JOB_FIELDS}
    updates['updated_at'] = _now()
    ref.update(updates)
    return _doc_to_dict(ref.get())


def job_delete(job_id):
    ref = _fs_col('jobs').document(str(job_id))
    if not ref.get().exists:
        return False
    ref.delete()
    return True


def job_bulk_delete(ids):
    from utils.firestore_manager import get_firestore_client as _gfc
    col = _fs_col('jobs')
    batch = _gfc().batch()
    for jid in ids:
        batch.delete(col.document(str(jid)))
    batch.commit()
    return len(ids)


def job_count():
    return len(list(_fs_col('jobs').stream()))


def job_count_by_status():
    rows = [_doc_to_dict(d) for d in _fs_col('jobs').stream() if d.to_dict()]
    counts = {'Applied': 0, 'Interview': 0, 'Offer': 0, 'Rejected': 0}
    for r in rows:
        s = r.get('status', 'Applied')
        if s in counts:
            counts[s] += 1
    return counts


# ── CONTACT MESSAGE ────────────────────────────────────────────────────────────

def message_list():
    docs = _fs_col('contact_messages').stream()
    rows = [_doc_to_dict(d) for d in docs if d.to_dict()]
    rows.sort(key=lambda r: r.get('created_at') or '', reverse=True)
    return rows


def message_get(msg_id):
    doc = _fs_col('contact_messages').document(str(msg_id)).get()
    if not doc.exists:
        return None
    return _doc_to_dict(doc)


def message_create(data):
    new_id = _next_id('contact_messages')
    now = _now()
    doc = {
        'id': new_id,
        'name': data.get('name') or '',
        'email': data.get('email') or '',
        'subject': data.get('subject') or '',
        'message': data.get('message') or '',
        'is_read': False,
        'created_at': now,
    }
    _fs_col('contact_messages').document(str(new_id)).set(doc)
    return dict(doc)


def message_set_read(msg_id, is_read):
    ref = _fs_col('contact_messages').document(str(msg_id))
    if not ref.get().exists:
        return False
    ref.update({'is_read': bool(is_read)})
    return True


def message_delete(msg_id):
    ref = _fs_col('contact_messages').document(str(msg_id))
    if not ref.get().exists:
        return False
    ref.delete()
    return True


def message_bulk_delete(ids):
    from utils.firestore_manager import get_firestore_client as _gfc
    col = _fs_col('contact_messages')
    batch = _gfc().batch()
    for mid in ids:
        batch.delete(col.document(str(mid)))
    batch.commit()
    return len(ids)


def message_count():
    return len(list(_fs_col('contact_messages').stream()))


def message_count_unread():
    docs = _fs_col('contact_messages').stream()
    return sum(1 for d in docs if not (d.to_dict() or {}).get('is_read', False))


# ── JOB POST ──────────────────────────────────────────────────────────────────

def _clean1(v):
    if not v:
        return v
    try:
        from utils.job_aggregator import clean_text
        return clean_text(v, multiline=False)
    except Exception:
        return v


def _cleanm(v):
    if not v:
        return v
    try:
        from utils.job_aggregator import clean_text
        return clean_text(v, multiline=True)
    except Exception:
        return v


def _jobpost_doc_to_dict(doc):
    d = doc.to_dict()
    if d is None:
        return None
    d['id'] = int(doc.id) if str(doc.id).isdigit() else doc.id
    return d


def _jobpost_to_api(d):
    """Convert a raw Firestore dict to the API dict format (tags as list)."""
    if d is None:
        return None
    raw_tags = d.get('tags') or ''
    if isinstance(raw_tags, list):
        tag_list = [_clean1(t.strip()) for t in raw_tags if t.strip()]
    else:
        tag_list = [_clean1(t.strip()) for t in raw_tags.split(',') if t.strip()]
    desc = _cleanm(d.get('description') or d.get('original_description') or '')
    return {
        'id': d.get('id'),
        'external_id': d.get('external_id') or '',
        'source': _clean1(d.get('source') or 'manual'),
        'title': _clean1(d.get('title') or ''),
        'company': _clean1(d.get('company') or ''),
        'location': _clean1(d.get('location') or ''),
        'job_type': _clean1(d.get('job_type') or ''),
        'salary': _clean1(d.get('salary') or ''),
        'tags': tag_list,
        'apply_url': _clean1(d.get('apply_url') or ''),
        'description': desc,
        'original_description': d.get('original_description') or '',
        'ai_rewritten': bool(d.get('ai_rewritten', False)),
        'status': d.get('status') or 'draft',
        'featured': bool(d.get('featured', False)),
        'created_at': d.get('created_at'),
        'updated_at': d.get('updated_at'),
    }


def jobpost_list(status=None, featured=None, limit=None, ai_rewritten=None):
    docs = list(_fs_col('job_posts').stream())
    rows = []
    for doc in docs:
        d = _jobpost_doc_to_dict(doc)
        if d is None:
            continue
        if status is not None and d.get('status') != status:
            continue
        if featured is not None and bool(d.get('featured', False)) != featured:
            continue
        if ai_rewritten is not None and bool(d.get('ai_rewritten', False)) != ai_rewritten:
            continue
        rows.append(d)
    rows.sort(key=lambda r: (
        0 if r.get('featured') else 1,
        r.get('updated_at') or '',
    ), reverse=True)
    if limit:
        rows = rows[:limit]
    return [_jobpost_to_api(r) for r in rows]


def jobpost_list_raw(status=None, ai_rewritten=None, limit=None):
    """Return raw Firestore dicts (not API-formatted) for internal use."""
    docs = list(_fs_col('job_posts').stream())
    rows = []
    for doc in docs:
        d = _jobpost_doc_to_dict(doc)
        if d is None:
            continue
        if status is not None and d.get('status') != status:
            continue
        if ai_rewritten is not None and bool(d.get('ai_rewritten', False)) != ai_rewritten:
            continue
        rows.append(d)
    rows.sort(key=lambda r: r.get('updated_at') or '', reverse=True)
    if limit:
        rows = rows[:limit]
    return rows


def jobpost_get(post_id):
    doc = _fs_col('job_posts').document(str(post_id)).get()
    if not doc.exists:
        return None
    d = _jobpost_doc_to_dict(doc)
    return _jobpost_to_api(d)


def jobpost_get_raw(post_id):
    doc = _fs_col('job_posts').document(str(post_id)).get()
    if not doc.exists:
        return None
    return _jobpost_doc_to_dict(doc)


def jobpost_create(data):
    new_id = _next_id('job_posts')
    now = _now()
    tags = data.get('tags', '')
    if isinstance(tags, list):
        tags = ', '.join(tags)
    doc = {
        'id': new_id,
        'external_id': data.get('external_id') or '',
        'source': data.get('source') or 'manual',
        'title': data.get('title') or '',
        'company': data.get('company') or '',
        'location': data.get('location') or '',
        'job_type': data.get('job_type') or '',
        'salary': data.get('salary') or '',
        'tags': tags,
        'apply_url': data.get('apply_url') or '',
        'original_description': data.get('original_description') or '',
        'description': data.get('description') or '',
        'ai_rewritten': bool(data.get('ai_rewritten', False)),
        'status': data.get('status') or 'draft',
        'featured': bool(data.get('featured', False)),
        'created_at': now,
        'updated_at': now,
    }
    _fs_col('job_posts').document(str(new_id)).set(doc)
    return _jobpost_to_api(doc)


def jobpost_update(post_id, data):
    ref = _fs_col('job_posts').document(str(post_id))
    doc = ref.get()
    if not doc.exists:
        return None
    updates = {}
    for k, v in data.items():
        if k in _JOBPOST_FIELDS:
            if k == 'tags' and isinstance(v, list):
                v = ', '.join(v)
            if k == 'featured':
                v = bool(v)
            if k == 'ai_rewritten':
                v = bool(v)
            updates[k] = v
    updates['updated_at'] = _now()
    ref.update(updates)
    d = _jobpost_doc_to_dict(ref.get())
    return _jobpost_to_api(d)


def jobpost_delete(post_id):
    ref = _fs_col('job_posts').document(str(post_id))
    if not ref.get().exists:
        return False
    ref.delete()
    return True


def jobpost_bulk(ids, action):
    from utils.firestore_manager import get_firestore_client as _gfc
    col = _fs_col('job_posts')
    fs = _gfc()
    batch = fs.batch()
    affected = 0
    for pid in ids:
        ref = col.document(str(pid))
        if action == 'delete':
            batch.delete(ref)
        else:
            batch.update(ref, {'status': action, 'updated_at': _now()})
        affected += 1
    batch.commit()
    return affected


def jobpost_count_by_status():
    docs = list(_fs_col('job_posts').stream())
    counts = {'draft': 0, 'published': 0, 'archived': 0}
    for doc in docs:
        d = doc.to_dict()
        if d:
            s = d.get('status', 'draft')
            if s in counts:
                counts[s] += 1
    counts['total'] = sum(counts.values())
    return counts


def jobpost_count(status=None, ai_rewritten=None):
    docs = list(_fs_col('job_posts').stream())
    count = 0
    for doc in docs:
        d = doc.to_dict()
        if not d:
            continue
        if status is not None and d.get('status') != status:
            continue
        if ai_rewritten is not None and bool(d.get('ai_rewritten', False)) != ai_rewritten:
            continue
        count += 1
    return count


def jobpost_find_by_external_id(external_id):
    if not external_id:
        return None
    docs = list(_fs_col('job_posts').where('external_id', '==', external_id).limit(1).stream())
    if docs:
        d = _jobpost_doc_to_dict(docs[0])
        return _jobpost_to_api(d)
    return None


# ── CONTENT REPORTS ───────────────────────────────────────────────────────────

_REPORT_STATUSES = {'pending', 'reviewed', 'dismissed'}


def report_create(data):
    new_id = _next_id('content_reports')
    now = _now()
    doc = {
        'id': new_id,
        'content_type': data.get('content_type') or 'unknown',
        'content_id': str(data.get('content_id') or ''),
        'content_snippet': (data.get('content_snippet') or '')[:500],
        'reason': data.get('reason') or 'other',
        'details': (data.get('details') or '')[:1000],
        'status': 'pending',
        'created_at': now,
        'reviewed_at': None,
    }
    _fs_col('content_reports').document(str(new_id)).set(doc)
    return dict(doc)


def report_list(status=None):
    docs = _fs_col('content_reports').stream()
    rows = [_doc_to_dict(d) for d in docs if d.to_dict()]
    rows = [r for r in rows if r is not None]
    if status:
        rows = [r for r in rows if r.get('status') == status]
    rows.sort(key=lambda r: r.get('created_at') or '', reverse=True)
    return rows


def report_get(report_id):
    doc = _fs_col('content_reports').document(str(report_id)).get()
    if not doc.exists:
        return None
    return _doc_to_dict(doc)


def report_update_status(report_id, status):
    if status not in _REPORT_STATUSES:
        return None
    ref = _fs_col('content_reports').document(str(report_id))
    if not ref.get().exists:
        return None
    ref.update({'status': status, 'reviewed_at': _now()})
    return _doc_to_dict(ref.get())


def report_delete(report_id):
    ref = _fs_col('content_reports').document(str(report_id))
    if not ref.get().exists:
        return False
    ref.delete()
    return True


def report_count(status=None):
    rows = report_list(status=status)
    return len(rows)
