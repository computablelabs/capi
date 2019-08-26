from app import app

def main():
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])

if __name__ == '__main__':
    main()
