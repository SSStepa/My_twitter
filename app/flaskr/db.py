import os

import click
from flask import current_app, g




def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



def init_db():

    with current_app.open_resource('schema.sql') as f:
        cur = g.cur
        cur.execute(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
