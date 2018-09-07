#!/usr/bin/env python
from flask import (
    Flask, render_template, Response, Blueprint, flash, g, redirect, request, url_for, session
)
from .camera import Camera
from .auth import login_required

bp = Blueprint('video', __name__)

@bp.route('/', methods=('GET', 'POST'))
@login_required
def video_html():
    session.setdefault('ip', None)
    if request.method == 'POST':
        session['ip']=request.form['ip']
    return render_template('video.html')

import time
def gen(camera):
    while True:
        time.sleep(0.01)
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@bp.route('/video_feed')
def video_feed():
    camera = Camera(session['ip'])
    if camera.has_opened():
        return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
