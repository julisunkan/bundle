import json
import re
from utils.ai_engine import analyze_match, analyze_job_description


def parse_json_safely(text):
    if not text:
        return None
    try:
        text = text.strip()
        # Strip all code fences (```json ... ``` or ``` ... ```)
        text = re.sub(r'```(?:json)?\s*', '', text).strip().rstrip('`').strip()
        # Try parsing as-is first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Fall back: find outermost JSON object { } or array [ ]
        for open_c, close_c in [('{', '}'), ('[', ']')]:
            start = text.find(open_c)
            end   = text.rfind(close_c)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass
    except Exception:
        pass
    return None


def get_match_analysis(resume_text, job_description):
    raw = analyze_match(resume_text, job_description)
    data = parse_json_safely(raw)
    if data and isinstance(data, dict):
        return {
            'score': float(data.get('score', 0)),
            'missing_keywords': data.get('missing_keywords', []),
            'suggestions': data.get('suggestions', []),
        }
    return {
        'score': 0,
        'missing_keywords': [],
        'suggestions': ['Could not parse analysis. Please try again.'],
        'raw': raw
    }


def get_job_analysis(job_description):
    raw = analyze_job_description(job_description)
    data = parse_json_safely(raw)
    if data and isinstance(data, dict):
        return {
            'required_skills': data.get('required_skills', []),
            'keywords': data.get('keywords', []),
            'experience_level': data.get('experience_level', 'Not specified'),
            'key_responsibilities': data.get('key_responsibilities', []),
        }
    return {
        'required_skills': [],
        'keywords': [],
        'experience_level': 'Not specified',
        'key_responsibilities': [],
        'raw': raw
    }
