#!/bin/bash

cd /app
python run.py && celery -A celery_worker.celery worker --loglevel=info