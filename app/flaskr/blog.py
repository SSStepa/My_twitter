from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    g.cur.execute(
        'SELECT "post".id, title, body, created, author_id, username,'
        '(SELECT COUNT(*) FROM "post_like" WHERE post_id = "post".id) AS like_count'
        ' FROM "post" INNER JOIN "user" ON "post".author_id = "user".id'
        ' ORDER BY created DESC;'
    )
    posts = g.cur.fetchall()
    g.cur.execute(
        'SELECT user_id, post_id FROM "post_like" JOIN "user" ON "user".id = user_id'
    )
    likes = g.cur.fetchall()
    likes_dict = dict()
    for like in likes:
        key = like[1]
        if key not in likes_dict:
            likes_dict[key] = []
        likes_dict[key].append(like[0])
    tags_dict = dict()
    for post in posts:
        key = post[0]
        tags_dict[key] = tags_list(key)
    return render_template('blog/index.html', posts=posts, likes_dict=likes_dict, tags_dict=tags_dict)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tags = request.form['tags']
        if tags:
            tags = tags.split(" ")
            tags = set(tags)
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            g.cur.execute(
                'INSERT INTO "post" (title, body, author_id)'
                ' VALUES (%s, %s, %s) RETURNING id',
                (title, body, g.user[0],)
            )
            post_id = g.cur.fetchone()[0]
            if tags:
                for tag in tags:
                    g.cur.execute(
                        'INSERT INTO "tags" (tag, post_id)'
                        ' VALUES (%s, %s)',
                        (tag, post_id)
                    )
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    g.cur.execute(
        'SELECT "post".id, title, body, created, author_id, username'
        ' FROM "post" JOIN "user" ON "post".author_id = "user".id'
        ' WHERE "post".id = %s',
        (id,)
    )
    post_list = g.cur.fetchall()
    post = []
    for i in post_list[0]:
        post.append(i)
    g.cur.execute(
        'SELECT tag FROM "tags" WHERE post_id = %s',
        (id,)
    )
    tags = g.cur.fetchall()
    if tags:
        for i in tags:
            post.append(i[0])
    else:
        post.append("")
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post[4] != g.user[0]:
        abort(403)
    
    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tags = request.form['tags']
        if tags:
            tags = tags.split(" ")
            tags = set(tags)
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            g.cur.execute(
                'UPDATE "post" SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )
            g.cur.execute('DELETE FROM "tags" WHERE post_id = %s', (id,))
            if tags:
                for tag in tags:
                    g.cur.execute(
                        'INSERT INTO "tags" (post_id, tag)'
                        ' VALUES (%s, %s)',
                        (id, tag)
                    )
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    g.cur.execute('DELETE FROM "tags" WHERE post_id = %s', (id,))
    g.cur.execute('DELETE FROM "post" WHERE id = %s', (id,))
    g.cur.execute('DELETE FROM "post_like" WHERE post_id = %s', (id,))
    return redirect(url_for('blog.index'))


@bp.route('/<int:post_id>')
def like(post_id):

    """ This function toggles like to post."""

    user_id = g.user[0]
    g.cur.execute(
        'SELECT id FROM "post_like" WHERE user_id = %s and post_id = %s',
        (user_id, post_id)
    )
    likes = g.cur.fetchall()
    if likes:
        g.cur.execute(
            'DELETE FROM  "post_like" WHERE user_id = %s and post_id = %s',
            (user_id, post_id)
        )
    else:
        g.cur.execute(
            'INSERT INTO "post_like" (user_id, post_id)'
            ' VALUES (%s, %s)',
            (user_id, post_id)
        )

    return redirect(url_for('blog.index'))


def tags_list(post_id):
    g.cur.execute(
        'SELECT tag FROM "tags" WHERE post_id = %s',
        (post_id,)
    )
    tags = g.cur.fetchall()
    return [x[0] for x in tags]


@bp.route('/tag/<tag>')
def tag_find(tag):

    """Finds post with this tag"""

    g.cur.execute(
        'SELECT post_id FROM "tags" WHERE tag = %s',
        (tag,)
    )
    posts_id = g.cur.fetchall()
    posts = []
    for post_id in posts_id:
        g.cur.execute(
            'SELECT "post".id, title, body, created, author_id, username,'
            '(SELECT COUNT(*) FROM "post_like" WHERE post_id = "post".id) AS like_count'
            ' FROM "post" INNER JOIN "user" ON post.author_id = "user".id'
            ' WHERE "post".id = %s',
            (post_id,)
        )
        post = g.cur.fetchone()
        g.cur.execute(
            'SELECT user_id, post_id FROM "post_like" JOIN "user" ON "user".id = user_id'
        )
        likes = g.cur.fetchall()
        likes_dict = dict()
        for like in likes:
            key = like[1]
            if key not in likes_dict:
                likes_dict[key] = []
            likes_dict[key].append(like[0])
        tags_dict = dict()
        key = post[0]
        tags_dict[key] = tags_list(key)
        post_dict = { "post": post, "likes": likes_dict, "tags": tags_dict}
        posts.append(post_dict)
    return render_template('blog/finder.html', posts=posts, tag=tag)