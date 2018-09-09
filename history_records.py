import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .db import get_db
from datetime import datetime

bp = Blueprint('history_records', __name__, url_prefix='/history_records')

# @bp.route('/produce', methods=('GET', 'POST'))
def produce_record(db, criminal_id, user_id, camera_id):
    '''生成一条警示记录'''
    # db = get_db()
    last_time = db.execute(
        'SELECT time FROM history_records WHERE criminal_id = ? AND user_id = ? AND camera_id = ? ORDER BY time DESC',
        (criminal_id, user_id, camera_id)
    ).fetchone()

    current_time = datetime.now()
    if last_time is None or \
            ((current_time-datetime.strptime(last_time['time'], "%Y-%m-%d %H:%M:%S")).seconds >= 60 * 5):
        #如果和上次记录时间相差5分钟以上，则生成新的一条记录
        db.execute(
            'INSERT INTO history_records(criminal_id, time, user_id, camera_id)'
            'VALUES (?, ?, ?, ?)',
            (criminal_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, camera_id)
        )
        db.commit()

def get_history_records(user_id):
    '''获取用户user_id的所有历史记录'''
    db = get_db()
    records = db.execute(
        'SELECT r.id, u.username as username, c.name as criminal_name, '
        'c.id as criminal_id, c.important as criminal_important, r.time,'
        'r.camera_id FROM user u, criminal c, history_records r '
        'WHERE r.criminal_id = c.id and r.user_id = u.id and u.id = ?'
        'ORDER BY r.time DESC ',
        (user_id,)
    )
    return records

@bp.route('/manage', methods=('GET', 'POST'))
def manage():
    '''返回历史警示记录界面'''
    user_id = session.get('user_id')
    return render_template('history_records.html', records=get_history_records(user_id))

@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
def delete(id):
    '''删除某条历史记录'''
    db = get_db()
    db.execute('DELETE FROM history_records WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('history_records.manage'))