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
    @api.response(404, C.SERVER_ERROR)
    @api.response(408, C.SERVER_ERROR)
    def get(self, id):
        """
        Given a celery task uuid, instantiate an AsyncResult and return
        its status to the caller
        """
        try:
            task = self.get_task(id)
        except:
            current_app.logger.info(f'Celery task {id} could not be found')
            api.abort(404, (C.CELERY_TASK_NOT_FOUND % id))

        stat = task.status
        res = None

        if stat == C.SUCCESS or stat == C.FAILURE:
            if stat == C.SUCCESS:
                # when, successful there will be a tx_hash we can return
                try:
                    # we'll give it 5 seconds
                    res = task.get(C.CELERY_TASK_TIMEOUT)
                except Timeout:
                    # TODO different error code?
                    current_app.logger.info(f'Celery task {id} timed out during get attempt')
                    api.abort(408, (C.CELERY_TASK_TIMED_OUT % id))


            # regardless of succeed or failure, both are terminal and this task may be removed from persistance
            task.forget()
            current_app.logger.info(f'Celery task {id} fetched and forgotten')

        return dict(message=(C.CELERY_TASK_FETCHED % id), status=stat, result=res), 200

    def get_task(self, id):
        """
        Abstraction for fetching the actual celery task, easy to mock.
        """
        return AsyncResult(id, backend=current_app.config['CELERY_RESULT_BACKEND'])
