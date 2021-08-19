#!/usr/bin/env python3
from lib import db
from api.api import app

db.init()
app.run()
