#!/bin/bash

export ENV_PATH=$1
shift

./manage.py migrate
gunicorn -b 0.0.0.0:8000 $@
