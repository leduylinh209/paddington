#!/bin/bash
cd paddington/

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createcachetable

supervisord
