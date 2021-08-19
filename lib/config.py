import os

STIBBONS_DB_PATH=os.environ.get('STIBBONS_DB_PATH') or '/var/tmp/stibbons.db'
STIBBONS_LISTEN_ADDRESS=os.environ.get('STIBBONS_LISTEN_ADDRESS') or '0.0.0.0:5000'
STIBBONS_PROTOCOL_SCHEME=os.environ.get('STIBBONS_PROTOCOL_SCHEME') or 'https'
STIBBONS_ACCESS_LOG=bool(os.environ.get('STIBBONS_ACCESS_LOG'))
