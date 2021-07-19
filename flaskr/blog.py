import sqlite3

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    recipes = db.execute(
        'SELECT r.id, name, rcp_ingredients, text, rating, author_id, username'
        ' FROM recipe r JOIN user u ON r.author_id = u.id'
        ' ORDER BY rating DESC'
    ).fetchall()
    return render_template('blog/index.html', recipes=recipes)


def get_my_recipe(id, check_author=True):
    recipe = get_db().execute(
        'SELECT r.id, name, rcp_ingredients, text, rating, author_id, username'
        ' FROM recipe r JOIN user u ON r.author_id = u.id'
        ' WHERE r.id = ?',
        (id,)
    ).fetchone()

    if recipe is None:
        abort(404, f"Recipe id {id} doesn't exist.")

    if check_author and recipe['author_id'] != g.user['id']:
        abort(403, "Unauthorized for this function")
        # return redirect(url_for('auth.login'))
    return recipe


def get_recipe(id, check_author=True):
    recipe = get_db().execute(
        'SELECT r.id, name, rcp_ingredients, text, rating, author_id, username'
        ' FROM recipe r JOIN user u ON r.author_id = u.id'
        ' WHERE r.id = ?',
        (id,)
    ).fetchone()

    if recipe is None:
        abort(404, f"Recipe id {id} doesn't exist.")

    if check_author and recipe['author_id'] == g.user['id']:
        abort(403, "You can not rate your own recipe")
        # return redirect(url_for('auth.login'))
    return recipe


@bp.route('/create', methods=('GET', 'POST'))
@login_required
# @token_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        rcp_ingredients = request.form['rcp_ingredients']
        text = request.form['text']
        rating = request.form['rating']
        # author_id = current_user.id
        db = get_db()
        error = None

        if not name:
            error = 'Name is required'
        elif not rcp_ingredients:
            error = 'Ingredients are required'
        elif not text:
            error = 'Text is required'
        elif rating:
            error = 'You can not rate your own recipe'
        elif db.execute(
                'SELECT id FROM recipe WHERE name = ?', (name,)
        ).fetchone() is not None:
            error = f"Recipe {name} already exists."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO recipe (name, rcp_ingredients, text, rating, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, rcp_ingredients, text, rating, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


#  the recipe author can access and edit only his own recipe
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    recipe = get_my_recipe(id)

    if request.method == 'POST':
        name = request.form['name']
        rcp_ingredients = request.form['rcp_ingredients']
        text = request.form['rcp_ingredients']
        error = None

        if not name:
            error = 'Name is required.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'UPDATE recipe SET name = ?, rcp_ingredients = ?, text = ?'
                    ' WHERE id = ?',
                    (name, rcp_ingredients, text, id)
                )
                db.commit()
                return redirect(url_for('blog.index'))

    return render_template('blog/update.html', recipe=recipe)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_my_recipe(id)
    db = get_db()
    db.execute('DELETE FROM recipe WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


#  the recipe author can not access and rate his own recipe
@bp.route('/<int:id>/rate', methods=('GET', 'POST'))
@login_required
def rate(id):
    recipe = get_recipe(id)

    if request.method == 'POST':
        name = request.form['name']
        rating = int(request.form['rating'])
        error = None

        if not name:
            error = 'Name is required'
        elif not rating:
            error = 'Rating is required'
        elif rating not in range(1, 5):
            error = 'Rating is number between 1 and 5'                    # proveri jel upisuje

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'INSERT INTO recipe (name, rating)'
                    ' VALUES (?, ?)',
                    (name, rating)
                )
                recipe.r_sum += rating                                     #  dodala ovo
                recipe.r_count += 1
                recipe.rating = recipe.r_sum / recipe.r_count

                db.commit()
                return redirect(url_for('blog.index'))

    return render_template('blog/rate.html', recipe=recipe)


@bp.route('/all_recipes')
def all_recipes():
    db = get_db()
    result = db.execute(
        # "SELECT name FROM sqlite_master WHERE type='table';"
        'SELECT last_name, email, username, password FROM user;'
        # 'SELECT name FROM recipe;'
    )
    for name in result.fetchall():
        print(name[0])
        return ''
