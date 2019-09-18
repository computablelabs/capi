"""
use the same initialization steps as the app so that worker and app are talking
"""
from app import celery
from app.factory import create_app
from core.celery import initialize

# we don't pass celery here as to make the initialization step visible to worker
flask_app = create_app()
initialize(celery, flask_app)
