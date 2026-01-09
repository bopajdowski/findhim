FROM python:3.12.5 AS base

# Python Envs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME /code
WORKDIR $APP_HOME

RUN mkdir -p apps_static media
RUN useradd -m -d /home/django django
RUN chown -R django $APP_HOME
RUN chsh -s /bin/bash django
ENV PATH=/home/django/.local/bin:$PATH
USER django

# RUN apt-get update && apt-get install -y \
#     gdal-bin libgdal-dev \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements_*.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements_dev.txt

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
