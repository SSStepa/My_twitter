from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT "post".id, title, body, created, author_id, username,'
        '(SELECT COUNT(*) FROM "post_like" WHERE post_id = "post".id) AS like_count'
        ' FROM "post" INNER JOIN "user" ON post.author_id = "user".id'
        ' ORDER BY created DESC;'
    ).fetchall()
    likes = db.execute(
        'SELECT user_id, post_id FROM "post_like" JOIN "user" ON "user".id = user_id'
    ).fetchall()
    likes_dict = dict()
    for like in likes:
        key = like['post_id']
        if key not in likes_dict:
            likes_dict[key] = []
        likes_dict[key].append(like['user_id'])
    return render_template('blog/index.html', posts=posts, likes_dict=likes_dict)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tegs = request.form['tegs']
        tegs = tegs.split(" ")
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            post_id = db.execute(
                'INSERT INTO "post" (title, body, author_id)'
                ' VALUES (%s, %s, %s) RETURNING *',
                (title, body, g.user['id'],)
            )
#            raise Exception(post_id)
#            for teg in tegs:
#                db.execute (
#                    'INSERT INTO tegs (teg, id)'
 #                   ' VALUES (%s, %s)',
  #                  (teg, post_id)
  #              )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT "post".id, title, body, created, author_id, username'
        ' FROM "post" JOIN "user" ON "post".author_id = "user".id'
        ' WHERE p.id = %s',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tegs = request.form['tegs']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, tegs, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM "post" WHERE id = %s', (id,))
    db.execute('DELETE FROM "post_like" WHERE id = %s', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:post_id>')
def like(post_id):

    """ This function toggles like to post."""

    db = get_db()
    user_id = g.user['id']
    likes = db.execute(
        'SELECT id FROM "post_like" WHERE user_id = %s and post_id = %s',
        (user_id, post_id)
    ).fetchall()
    if likes:
        db.execute(
            'DELETE FROM  "post_like" WHERE user_id = %s and post_id = %s',
            (user_id, post_id)
        )
    else:
        db.execute(
            'INSERT INTO "post_like" (user_id, post_id)'
            ' VALUES (%s, %s)',
            (user_id, post_id)
        )


    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<teg>')
def teg_list(teg):
    s=1
