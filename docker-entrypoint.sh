#!/bin/bash
set -e

case $1 in
 runserver)
  cd /rapidpro; python manage.py runserver 0.0.0.0:8000
  ;;
 uwsgi_server)
  uwsgi  --socket app.sock --wsgi-file temba/wsgi.py --chmod-socket=666
  ;;
 supervisor)
  /usr/bin/supervisord -n -c /rapidpro/supervisor-app.conf
  ;;
esac

exec "$@"

