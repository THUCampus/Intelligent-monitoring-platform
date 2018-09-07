#!/usr/bin/env python
from flask import (
    Flask, render_template, Response, Blueprint, flash, g, redirect, request, url_for, session
)
from opencv_camera import Camera

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

@app.route('/', methods=('GET', 'POST'))
def index():
    session.setdefault('ip', None)
    session
    if request.method == 'POST':
        session['ip']=request.form['ip']
    return render_template('index.html')

import time
def gen(camera):
    while True:
        time.sleep(0.01)
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    camera = Camera(session['ip'])
    if camera.has_opened():
        return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)