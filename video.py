#!/usr/bin/env python
from flask import (
    render_template, Response, Blueprint, request, session, current_app
)
import sqlite3
from .camera import Camera
from .auth import login_required
from .history_records import produce_record, get_history_records
from .db import get_db_by_config

bp = Blueprint('video', __name__)

@bp.route('/', methods=('GET', 'POST'))
@login_required
def video_html():
    '''返回监控界面'''
    session.setdefault('ip', None)
    if request.method == 'POST':
        session['ip']=request.form['ip']
    user_id = session.get('user_id')
    return render_template('video.html',
                           records=get_history_records(user_id).fetchmany(5)) #监控页面只会显示最近的5条数据

import time
def gen(camera,config,user_id, camera_id):
    '''camera视频生成器'''
    while True:
        time.sleep(0.01)
        frame, criminal_ids = camera.get_frame(process={'face_recognition':2})
        for criminal_id in criminal_ids:
            db = get_db_by_config(config)
            produce_record(db, criminal_id=criminal_id, user_id=user_id, camera_id=camera_id)  # 设置camera_id暂时为0
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@bp.route('/video_feed')
def video_feed():
    '''返回监控界面中的视频部分'''
    camera = Camera(ip=session.get('ip'))
    user_id = session.get('user_id')
    camera_id = 0
    if not camera.has_opened():
        camera = Camera(0)
    return Response(gen(camera,config=current_app.config['DATABASE'], user_id=user_id, camera_id=camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
