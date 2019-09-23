from flask import g, current_app
from flask_restplus import Namespace, Resource
from celery.result import AsyncResult
from celery.exceptions import TimeoutError as Timeout
import core.constants as C
from .parsers import task_parser
from .serializers import TaskResult

api = Namespace('Tasks', description='Operations pertaining to celery asyncronous tasks')

api.models['TaskResult'] = TaskResult

@api.route('/<string:id>', methods=['GET'])
class TaskRoute(Resource):
    @api.expect(task_parser)
    @api.marshal_with(TaskResult)
    @api.response(200, C.CELERY_TASK_FETCHED)
    @api.response(500, C.SERVER_ERROR)
    def get(self, id):
        """
        Given a celery task uuid, instantiate an AsyncResult and return
        its status to the caller
        """
        task = AsyncResult(id, backend=current_app.config['CELERY_RESULT_BACKEND'])
        stat = task.status
        res = None

        if stat == 'SUCCESS':
            # since we are done here, this should not block
            try:
                # we'll give it 5 seconds
                res = task.get(C.CELERY_TASK_GET_TIMEOUT)
                # once a task has been fetched as done, remove it
                task.forget()
                current_app.logger.info(f'Celery task {id} fetched and forgotten')
            except Timeout:
                # TODO different error code?
                current_app.logger.info(f'Celery task {id} timed out during get attempt')
                api.abort(500, (C.SERVER_ERROR % 'Asynchronous task timed out'))

        # cleanup the var just in case
        task = None

        return dict(message=(C.CELERY_TASK_FETCHED % id), status=stat, result=res), 200
