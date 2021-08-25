import os
from typing import List

from lib import db

def access_log() -> bool:
    return bool(os.environ.get('STIBBONS_ACCESS_LOG'))

def protocol_scheme() -> str:
    return os.environ.get('STIBBONS_PROTOCOL_SCHEME') or 'https'

def listen_address() -> str:
    return os.environ.get('STIBBONS_LISTEN_ADDRESS') or '0.0.0.0:5000'

def email_allowlist() -> List[str]:
    allowlist_raw = os.environ.get('STIBBONS_EMAIL_ALLOWLIST')
    if allowlist_raw:
        return allowlist_raw.split(',')
    else:
        return [each['email_address'] for each in db.get_allowlist()]

def db_base_path() -> str:
    return os.environ.get('STIBBONS_DB_PATH') or './stibbons.db'
