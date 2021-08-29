import os

def access_log() -> bool:
    return bool(os.environ.get('STIBBONS_ACCESS_LOG'))

def protocol_scheme() -> str:
    return os.environ.get('STIBBONS_PROTOCOL_SCHEME') or 'https'

def listen_address() -> str:
    return os.environ.get('STIBBONS_LISTEN_ADDRESS') or '0.0.0.0:5000'

def db_base_path() -> str:
    return os.environ.get('STIBBONS_DB_PATH') or './stibbons.db'
