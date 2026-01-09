# Image
FROM python:3.12.5 as base

# Python Envs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Envs
ENV APP_HOME /code

# Packages  (run any apt-get install here)
# RUN apt-get update
# RUN apt-get install -y gdal-bin libgdal-dev
# RUN rm -rf /var/lib/apt/lists/*

# User (required for file permissions between docker and local machine)
WORKDIR $APP_HOME
RUN mkdir apps_static
RUN mkdir media

# Development requirements copy
COPY requirements_*.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements_prod.txt

# Project Requirements copy
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt


# Backend
FROM base AS backend

COPY . ./
ENTRYPOINT ["./Docker/entrypoint.sh"]

## Celery
#FROM base AS celery
#
#COPY . ./
#CMD ["celery", "-A", "project", "worker", "--loglevel=INFO"]
#
## Celery Beat
#FROM base AS celery-beat
#
#COPY . ./
#CMD ["celery", "-A", "project", "beat", "--loglevel=INFO"]