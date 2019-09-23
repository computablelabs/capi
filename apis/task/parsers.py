from flask_restplus import reqparse

task_parser = reqparse.RequestParser()
task_parser.add_argument('id', type=str, required=True, location='args', help='UUID of a previously started asynchronous task')

