#!/usr/bin/python
from wsgiref.handlers import CGIHandler
from search import app

CGIHandler().run(app)
