from flask_restplus import reqparse

task_parser = reqparse.RequestParser()
task_parser.add_argument('id', type=str, required=True, location='args', help='UUID of a previously started asynchronous task')

new_task = reqparse.RequestParser()
new_task.add_argument('tx_hash', type=str, required=True, location='json', help='Transaction hash which to indicate mining status of')
