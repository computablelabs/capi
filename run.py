from app import celery as c
from app.factory import create_app

def main():
    flask_app = create_app(celery=c)
    flask_app.run(
        debug=flask_app.config['DEBUG'],
        host=flask_app.config['HOST'],
        port=flask_app.config['PORT'])

if __name__ == '__main__':
    main()
