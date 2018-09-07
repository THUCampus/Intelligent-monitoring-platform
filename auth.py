import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET','POST'))
def login():
    '''登录界面'''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = '错误的用户名.'
        elif not check_password_hash(user['password'], password):
            error = '错误的密码.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('video.video_html'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    '''载入最近登录过的用户信息'''
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    '''用户登出'''
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    '''至少是普通用户权限才可以返回的页面装饰器'''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def manager_required(view):
    # '''拥有管理员权限才可以返回的页面装饰器'''
    # @functools.wraps(view)
    # def wrapped_view(**kwargs):
    #     if g.user is None:
    #         return redirect(url_for('auth.login'))
    #     elif not g.user['is_manager']:
    #         return redirect(url_for('video.video_html'))
    #
    #     return view(**kwargs)
    # return wrapped_view
    '''至少是普通用户权限才可以返回的页面装饰器'''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@manager_required
@bp.route('/register', methods=('GET', 'POST'))
def register():
    '''注册界面'''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_manager = True if request.form['is_manager'] == "True" else False

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, is_manager) VALUES (?,?,?)',
                (username, generate_password_hash(password), is_manager)
            )
            db.commit()
            return redirect(url_for('auth.manage'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/manage')
@manager_required
def manage():
    '''返回管理员界面'''
    db = get_db()
    user_id = session.get('user_id')
    users = db.execute(
        'SELECT u.id, u.username, u.is_manager FROM user u WHERE u.id != ?',(user_id,)
    )
    return render_template('auth/manage.html',users=users)

@bp.route('/<int:id>/delete', methods=('POST','GET'))
@manager_required
def delete(id):
    '''删除某个用户'''
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('auth.manage'))

@bp.route('/update_password', methods=('POST','GET'))
@login_required
def update_password():
    '''修改用户密码'''
    if request.method == 'POST':
        db = get_db()

        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        error = None

        if not username:
            error = '请填入用户名.'
        else:
            user = db.execute(
                'SELECT id, password FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                error = '用户{}不存在'.format(username)
            elif not check_password_hash(user['password'], old_password):
                error = "密码错误"

        if error is None:
            db.execute(
                'UPDATE user SET password = ? WHERE id = ?',
                (generate_password_hash(new_password), user['id'])
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/update_password.html')