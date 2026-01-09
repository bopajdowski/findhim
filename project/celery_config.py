"""Celery configuration."""
#
# # Standard Library
# import os
#
# # 3rd-Party
# from celery import Celery
# from environs import Env
#
# env = Env()
# env.read_env()
#
# # Setting up
# REDIS_URL = env.str('REDIS_URL', 'redis://redis:6379/0')
# # Configurations
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
# # Celery
# app = Celery(
#     'project',
#     broker=REDIS_URL,
#     backend=REDIS_URL,
# )
# app.conf.result_backend = REDIS_URL
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# # Task Finder
# app.autodiscover_tasks()
#
# app.conf.beat_schedule = {}
