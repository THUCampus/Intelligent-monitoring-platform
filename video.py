#!/usr/bin/env python
from flask import (
    render_template, Response, Blueprint, request, session, current_app
)
import time
from .camera import Camera
from .auth import login_required
from .history_records import produce_record, get_history_records
from .db import get_db_by_config,get_db
from .history_records import RecordsGenerator

bp = Blueprint('video', __name__)

'''
一些需要全局使用的变量
'''
box_selection=[0,0,0,0]

@bp.route('/', methods=('GET', 'POST'))
@login_required
def video_html():
    '''返回监控界面'''
    session.setdefault('ip', "0")
    session.setdefault('camera_id', '0')
    session.setdefault('task', "face_recognition")
    session.setdefault('interval', 5)
    global box_selection
    box_selection=[0,0,0,0]
    if request.method == 'POST':
        if request.form['form_type'] == 'box_selection':
            box_selection=[int(x)*32/45 for x in request.form['box_selection'].split('_')]
        elif request.form['form_type'] == "ip":
            session['ip']=request.form['ip']
            session['camera_id'] = request.form['camera_id']
        elif request.form['form_type'] == 'task':
            session['task'] = request.form['task']
        elif request.form['form_type'] == 'interval':
            session['interval'] = request.form['interval']
    return render_template('video.html',
                           ip=session.get("ip"), camera_id = session.get("camera_id"),
                           task=session.get('task'), interval=session.get('interval'))


def gen(camera,config,user_id, camera_id,process,interval):
    '''camera视频生成器'''
    while True:
        time.sleep(0.01) # 每个0.01s推送一帧视频
        frame, criminal_ids = camera.get_frame(process=process)
        for criminal_id in criminal_ids:
            db = get_db_by_config(config)
            produce_record(db, criminal_id=criminal_id, user_id=user_id,
                           camera_id=camera_id,interval=interval)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@bp.route('/video_feed')
def video_feed():
    '''返回监控界面中的视频部分'''
    camera = Camera(ip=session.get('ip'))
    process = {session.get('task'):1,'box':box_selection}#获取图像的处理方式
    user_id = session.get('user_id')
    if not camera.has_opened():#如果打开失败
        session['ip'] = "0"
        camera = Camera("0")
    return Response(gen(camera,config=current_app.config['DATABASE'], user_id=user_id,
                        camera_id=session['camera_id'], process=process, interval=session.get('interval')),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/records_feed')
def records_feed():
    '''返回监控界面的警示记录部分'''
    user_id = session.get("user_id")
    return Response(RecordsGenerator(user_id=user_id,db_config=current_app.config['DATABASE']),
                    mimetype='text/event-stream')
