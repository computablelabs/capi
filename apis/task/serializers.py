from flask_restplus import Model, fields

TaskResult = Model('TaskResult', {
    'message': fields.String(required=True, description='Server response when an anyschronous task is fetched'),
    'status': fields.String(required=True, description='One of [STARTED, PENDING, FAILURE, SUCCESS]'),
    'result': fields.String(description='The result of the task if finished, likely an Ethereum transaction hash')
    })
