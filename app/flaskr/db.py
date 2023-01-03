import psycopg2
import os

import click
from flask import current_app, g

dbname=os.environ['POSTGRES_DB']
user=os.environ['POSTGRES_USER']
password=os.environ['POSTGRES_PASSWORD']
host=os.environ['POSTGRES_HOST']
port=int(os.environ['POSTGRES_PORT'])
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)


def get_db():

    if 'db' not in g:
        g.db = conn.cursor()
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
