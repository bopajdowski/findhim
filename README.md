# Project Setup

## Docker Compose for Local Development and Production

This repository provides a `docker-compose.yml` configuration tailored for local development or production environment of a Django application with NGINX, PostgreSQL, Redis, Celery, and Traefik.

---

## Features

- **NGINX**: Serves static and media files and acts as a reverse proxy for the backend.
- **Django Backend**: Configurable for development and production.
- **Redis**: In-memory data structure store, used as a message broker for Celery.
- **Celery**: Task queue for asynchronous tasks, with an optional scheduler (Celery Beat).
- **PostgreSQL**: Relational database management.
- **Traefik**: Handles routing in production environments with SSL.

---

## Directory/File Structure

- **`Docker/`**: Contains Dockerfiles and environment-specific configurations.
- **`project/`**: Contains Django configuration files.
- **`apps/`**: Empty folder in which you should put all your django applications.
- **`requirements_*.txt`**: Python dependencies.
- **`entrypoint.sh`**: Startup script for different environments.

---

## Prerequisites

1. **Docker**: Ensure Docker is installed.
2. **Docker Compose**: Ensure `docker-compose` is installed.
3. **Environment Variables**: Set required environment variables (e.g., `APP`, `SECRET_KEY`, `ENV`, etc.).

---

## Setup and Usage

### Enabling Additional Services

This configuration includes optional services such as Redis, Celery, and Celery Beat, which you can enable as needed for your project. Follow the steps below to activate these services.

---

### Step 1: Update `docker-compose.yml`

In the `services` section of `docker-compose.yml`, locate the following services:
- `redis`
- `celery-local`
- `celery`
- `celery-beat-local`
- `celery-beat`

Uncomment these service definitions to include them in your Docker Compose stack.

---

### Step 2: Update `Dockerfile`

If you plan to use Celery and Celery Beat, locate the `celery` and `celery-beat` stages in the `Dockerfile`. Uncomment the corresponding steps to ensure the required configurations are built into the images.

---

### Step 3: Modify `.env` File

Ensure the `.env` file includes any necessary environment variables for Redis and Celery. For example:

```dotenv
REDIS_URL=redis://redis:6379/0
```

### Environment Variables

Create a `.env` file in the root directory:

```dotenv
APP=django_template
ENV=dev
ENV_VERSION=dev
COMPOSE_PROFILES=dev,db
SECRET_KEY=example_secret_key
PORT=8000
```

### Start Development Services

1. Modify the `.env` file:
```dotenv
COMPOSE_PROFILES=dev,db  # runserver + optional db
```
or
```dotenv
COMPOSE_PROFILES=nginx,db  # gunicorn & nginx + optional db
```
2. Start the services:
```
docker compose up -d
```
Services started:

- `backend` (Django backend with Gunicorn or Runserver)
- `nginx` (Optional: Local NGINX)
- `redis` (Redis service - if used)
- `celery` (Celery worker - if used)
- `celery-beat` (Celery scheduler - if used)
- `database` (Optional: PostgreSQL)

### Start Production Services

To run the application in production mode, follow the steps below.

---

1. Update `.env` File

```dotenv
COMPOSE_PROFILES=prod
```

Services started:

- `backend` (Django backend with Gunicorn)
- `nginx` (Production-ready NGINX)
- `redis` (Redis service - if used)
- `celery` (Celery worker - if used)
- `celery-beat` (Celery scheduler - if used)
- `database` (Optional: PostgreSQL)

### Stop All Services
```
docker compose down
```

---

## Service Descriptions

### Backend
- **Local**: Development server via `runserver`.
- **Production**: Gunicorn application server.

### NGINX
- **Local**: Serves static files with a development configuration.
- **Production**: Integrates with Traefik for SSL and routing.

### Redis
Used as:
- A message broker for Celery.
- A caching backend for Django (optional).

### Celery
- **Celery**: Executes tasks asynchronously.
- **Celery Beat**: Periodic task scheduler.

### PostgreSQL
Stores persistent data for the Django application.

### Traefik
Handles:
- Routing in production environments.
- SSL certificate management via Let's Encrypt.

---

## Customization

### Modify Volumes
Adjust the volumes in `docker-compose.yml` as necessary for your development/production setup.

### Extend Django Configuration
Add additional Django settings to support caching, email services, and more by modifying the `settings.py` file.

---

## Profiles Overview

Profiles control which services are started:
- `dev`: Starts local development services (e.g., `backend-local`, `celery-local`).
- `prod`: Starts production services (e.g., `backend`, `celery`).
- `nginx`: Includes NGINX in the stack.
- `db`: Includes the PostgreSQL database.

Use the `COMPOSE_PROFILES` variable in the `.env` file to define active profiles.

---

## Useful Commands

### Check Logs
```bash
docker compose logs -f
```

### Restart Services
```bash
docker compose restart <service_name>
```
### Enter a Container
```bash
docker exec -it <container_name> bash
```

## Troubleshooting

- **Service Fails to Start**: Check `.env` file and ensure all required variables are set.
- **Static/Media Not Found**: Verify `static_volume` and `media_volume` are correctly mounted.
- **Database Issues**: Ensure `postgres_data` volume is not corrupted.
- **Redis Connection Error**: Verify that the Redis container is running and accessible via `redis://redis:6379/0`.

---

# Sentry

## Create Project

- Go to https://sentry.webtechnika.pl/organizations/webtechnika/projects/
- Click on **+ Create Project**
- Select **Django** and put desired name (best - repository name)
- Copy **DSN** url and set **SENTRY_DSN** environment variable in github action secrets.

## Edit Alert Rule

- Select newly created Alert rule from here https://sentry.webtechnika.pl/organizations/webtechnika/alerts/rules/?statsPeriod=14d
- Click on **Edit Rule**
- Remove default **Then** section and add new in that place - **Send a Slack notification**
- Then fill the form:

>Send a notification to the **webtechnika** Slack workspace to
**#errors** (optionally, an ID: **C07NT3EUTCY**)

- Save the rule by clicking button below **Save Rule**