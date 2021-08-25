#!/usr/bin/env python3
import logging
from waitress import serve
from lib import db, config
from api.api import app, ACCESS_LOGGER_NAME

db.init()
if config.access_log():
    logging.getLogger(ACCESS_LOGGER_NAME).setLevel(logging.INFO)
serve(app, listen=config.listen_address(), url_scheme=config.protocol_scheme())
