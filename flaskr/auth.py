import functools
from functools import wraps
import datetime

import jwt
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, app, current_app
from jwt import PyJWT

from werkzeug.security import check_password_hash, generate_password_hash

import flaskr
from flaskr.db import get_db
from flaskr.my_clearbit import get_user_and_company_data
from flaskr.my_hunter import email_verification

bp = Blueprint('auth', __name__, url_prefix='/auth')


# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'access_token' in request.headers:
#             token = request.headers['access_token']
#         if not token:
#             return jsonify({'message': 'Token is missing'}), 401
#
#         try:
#             data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             current_user = g.user.query.filter_by(id=data['id']).first()
#         except:
#             return jsonify({'message': 'Token is invalid.'}), 401
#
#         return f(current_user, *args, **kwargs)
#
#     return decorated


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not first_name:
            error = 'First name is required.'
        elif len(first_name) > 15:
            error = 'Please Fill This Field with max 15 characters.'
        elif not last_name:
            error = 'Last name is required.'
        elif len(last_name) > 20:
            error = 'Please Fill This Field with max 20 characters.'
        elif not email:
            error = 'Email is required.'
        elif len(email) > 30:
            error = 'Please Fill This Field with max 30 characters.'
        elif not username:
            error = 'Username is required.'
        elif len(username) > 15:
            error = 'Please Fill This Field with max 15 characters.'
        elif not password:
            error = 'Password is required.'
        elif len(password) > 200:
            error = 'Please Fill This Field with max 200 characters.'
        elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."

        email_verification(email)
        get_user_and_company_data(email)

        if error is None:
            db.execute(
                'INSERT INTO user (first_name, last_name, email, username, password) VALUES (?, ?, ?, ?, ?)',
                (first_name, last_name, email, username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        # elif check_password_hash(user['password'], password):
        #     token = jwt.encode(
        #         payload={'id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        #         key=current_app.config['SECRET_KEY'],
        #         algorithm='HS256')

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
            # return jsonify({'token': token}), 200

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
