from flask import current_app, g
from flask_restplus import Namespace, Resource
from celery import uuid
from celery.result import AsyncResult
from celery.exceptions import TimeoutError as Timeout
from app import celery as celery_app
from core.protocol import is_registered
import core.constants as C
from apis.tasks import wait_for_mining
from .parsers import new_task, task_parser
from .serializers import NewTaskResult, TaskResult

api = Namespace('Tasks', description='Operations pertaining to celery asyncronous tasks')

api.models['NewTaskResult'] = NewTaskResult
api.models['TaskResult'] = TaskResult

@api.route('/', methods=['POST'])
class NewTaskRoute(Resource):
    @api.expect(new_task)
    @api.marshal_with(NewTaskResult)
    @api.response(201, C.CELERY_TASK_CREATED)
    @api.response(400, C.MISSING_PAYLOAD_DATA)
    @api.response(500, C.NOT_REGISTERED)
    @api.response(504, C.TRANSACTION_TIMEOUT)
    def post(self):
        """
        Given a transaction hash, start an async task to monitor when it has mined.
        Once created users can use 'TaskRoute' to check its status.
        """
        if is_registered() == False:
            current_app.logger.error('POST new task called but this server is not the datatrust')
            api.abort(500, C.NOT_REGISTERED) # TODO different error code?
        else:
            args = new_task.parse_args()
            # must have a tx_hash
            tx = args['tx_hash']
            if not tx:
                current_app.logger.warning(C.MISSING_PAYLOAD_DATA % 'tx_hash')
                api.abort(400, (C.MISSING_PAYLOAD_DATA % 'tx_hash'))
            else:
                uid = self.start_task(tx)
                current_app.logger.info(C.NEW_LISTING_SUCCESS)

                return dict(message=(C.CELERY_TASK_CREATED % uid), task_id=uid), 201

    def start_task(self, tx_hash):
        uid = uuid()
        try:
            wait_for_mining.s(tx_hash).apply_async(task_id=uid)
        except Exception as e:
            api.abort(504, str(e))

        return uid

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
        return AsyncResult(id, app=celery_app)
