from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .db import get_db,get_db_by_config
from .auth import login_required
from . import history_records,intruding_records

bp = Blueprint('records', __name__, url_prefix='/records')

@bp.route('/manage', methods=('GET', 'POST'))
@login_required
def manage():
    '''返回历史警示记录界面'''
    session.setdefault('task', "face_recognition")
    if request.method == 'POST':
        session['task'] = request.form['task']
        print(session['task'])
    user_id = session.get('user_id')
    db = get_db()
    if session.get('task') == "face_recognition":
        return render_template('records.html',
                records=history_records.get_history_records(db, user_id),
                task=session.get("task"))
    elif session.get("task") == "object_track":
        return render_template('records.html',
                records=intruding_records.get_instruding_records(db, user_id),
                task=session.get("task"))
    else:#默认为罪犯追踪
        return render_template('records.html',
                records=history_records.get_history_records(db, user_id),
                task="face_recognition")



@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    '''删除某条历史记录'''
    db = get_db()
    if session.get('task') == "face_recognition":
        db.execute('DELETE FROM history_records WHERE id = ?', (id,))
    elif session.get("task") == "object_track":
        db.execute('DELETE FROM intruding_records WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('records.manage'))
