#!/bin/bash

source ../../shared/back/back-start-shared.sh

export FLASK_APP=main.py
if [ '$MIGRATION' == '1' ]; then
  flask db migrate
  flask db upgrade
fi

uwsgi --enable-threads --ini app/uwsgi.ini
#python -m debugpy --listen localhost:5678 --wait-for-client app/main.py
