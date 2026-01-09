#!/bin/bash

case "${COMPOSE_PROFILES}" in
  *prod*)
    python manage.py collectstatic --noinput
    python manage.py migrate
    ;;
esac

case "${COMPOSE_PROFILES}" in
  *nginx*|*prod*)
    gunicorn project.wsgi:application \
      --workers ${GUNICORN_WORKERS:-4} \
      --threads ${GUNICORN_THREADS:-1} \
      --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
      --bind 0.0.0.0:${PORT:-8000} \
      --access-logfile '-' --error-logfile '-'
    ;;
  *)
    python manage.py runserver 0.0.0.0:${PORT:-8000}
    ;;
esac