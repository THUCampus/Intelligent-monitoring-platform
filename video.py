#!/usr/bin/env python
from flask import (
    render_template, Response, Blueprint, request, session
)
from .camera import Camera
from .auth import login_required

bp = Blueprint('video', __name__)

@bp.route('/', methods=('GET', 'POST'))
@login_required
def video_html():
    '''返回监控界面'''
    session.setdefault('ip', None)
    if request.method == 'POST':
        session['ip']=request.form['ip']
    return render_template('video.html')

import time
def gen(camera):
    '''camera视频生成器'''
    while True:
        time.sleep(0.01)
        frame = camera.get_frame(process={'face_recognition':2})
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@bp.route('/video_feed')
def video_feed():
    '''返回监控界面中的视频部分'''
    camera = Camera(session['ip'])
    if camera.has_opened():
        return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(gen(Camera(0)),mimetype='multipart/x-mixed-replace; boundary=frame')
