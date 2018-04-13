#!/bin/bash

export TEMPLATES_AUTO_RELOAD=True
export FLASK_APP=app.py
flask run --debugger --reload
