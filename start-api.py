#!/usr/bin/env python3
import logging
from waitress import serve
from lib import db, config
from api.api import app, ACCESS_LOGGER_NAME

db.init()
if config.STIBBONS_ACCESS_LOG:
    logging.getLogger(ACCESS_LOGGER_NAME).setLevel(logging.INFO)
serve(app, listen=config.STIBBONS_LISTEN_ADDRESS, url_scheme=config.STIBBONS_PROTOCOL_SCHEME)
