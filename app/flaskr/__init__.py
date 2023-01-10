import os
import psycopg2
from flask import Flask, g

dbname=os.environ['POSTGRES_DB']
user=os.environ['POSTGRES_USER']
password=os.environ['POSTGRES_PASSWORD']
host=os.environ['POSTGRES_HOST']
port=int(os.environ['POSTGRES_PORT'])
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


    @app.before_request
    def before_request():
        g.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        g.cur = g.conn.cursor()
    

    @app.after_request
    def after_request(response):
        g.conn.commit()
        return response
    

    @app.teardown_request
    def teardown_request(exception):
        g.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        g.cur = g.conn.cursor()
        g.conn.rollback()

    return app
