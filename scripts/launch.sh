#!/bin/bash

cd /app
(celery -A celery_worker.celery worker --loglevel=info &) && python run.py