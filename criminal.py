from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import face_recognition,pickle,os

from .db import get_db
from .auth import login_required,manager_required

bp = Blueprint('criminal', __name__, url_prefix='/criminal')

@bp.route('/register', methods=('GET', 'POST'))
@manager_required
def register():
    '''逃犯信息录入界面'''
    if request.method == 'POST':
        name = request.form['criminal_name']
        id = request.form['criminal_id']
        photo= request.files['criminal_photo']

        #将上传的图片进行人脸编码，然后序列化存到数据库中
        photo.save(photo.filename)
        image = face_recognition.load_image_file(photo.filename)
        encoding = face_recognition.face_encodings(image)[0]
        encoding = pickle.dumps(encoding)
        os.remove(photo.filename)

        important = True if request.form['criminal_importance'] == "True" else False

        db = get_db()
        error = None

        if not name:
            error = 'Criminal name is required.'
        elif not encoding:
            error = 'Encoding is required.'
        elif db.execute(
                'SELECT rank FROM criminal WHERE id = ?', (id,)
        ).fetchone() is not None:
            error = 'Criminal {} whose id is {} is already registered.'.format(name, id)

        if error is None:
            db.execute(
                'INSERT INTO criminal (name, id, encoding, important) VALUES (?,?,?,?)',
                (name, id, encoding, important)
            )
            db.commit()
            return redirect(url_for('auth.manage'))

        flash(error)
    return render_template('criminal/register.html')


@bp.route('/manage')
@login_required
def manage():
    '''返回所有的逃犯'''
    db = get_db()
    criminals = db.execute(
        'SELECT id, name, important,rank FROM criminal'
    )
    return render_template('criminal/manage.html',criminals=criminals)


@bp.route('/<int:rank>/delete', methods=('POST','GET'))
@login_required
def delete(rank):
    '''删除某个罪犯'''
    db = get_db()
    db.execute('DELETE FROM criminal WHERE rank = ?', (rank,))
    db.commit()
    return redirect(url_for('criminal.manage'))
