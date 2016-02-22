#!/bin/bash
set -e

case $1 in
 runserver)
  cd /rapidpro; python manage.py syncdb;python manage.py runserver 0.0.0.0:8000
  ;;
 uwsgi_server)
  python manage.py syncdb
  uwsgi  --socket app.sock --wsgi-file temba/wsgi.py --chmod-socket=666
  ;;
 supervisor)
  python manage.py syncdb
  /usr/bin/supervisord -n -c /rapidpro/supervisor-app.conf
  ;;
esac

exec "$@"

