def initialize(celery, app):
    """
    we have to lazily initialize an existing celery app with our config
    """
    celery.conf.update({
        'result_backend': app.config['CELERY_RESULT_BACKEND'],
        'broker_url': app.config['CELERY_BROKER_URL']
        })

    class WithContext(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = WithContext
