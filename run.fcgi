#!/usr/bin/python
# Activate virtualenv used on Toolserver
activate_this = '/data/project/splinetools/venv-splinetools/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from flup.server.fcgi import WSGIServer
from splinetools import app

from flask import request

import time
import logging
from logging import FileHandler
logger = FileHandler('error.log')
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logger)
app.logger.debug(u"Flask server started " + time.asctime())


@app.after_request
def write_access_log(response):
    app.logger.debug(u"%s %s -> %s" % (time.asctime(), request.path, response.status_code))
    return response

if __name__ == '__main__':
    WSGIServer(app).run()