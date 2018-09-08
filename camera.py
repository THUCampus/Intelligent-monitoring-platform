import cv2

class Camera:
    '''IP 摄像头类'''
    def __init__(self, ip=None):
        self.camera = None
        if ip is not None:
            self.set_ip(ip)

    def set_ip(self, ip):
        '''设置摄像头的ip地址'''
        self.ip = ip
        if ip == "0": #打开系统摄像头
            self.camera = cv2.VideoCapture(0)
        else:
            self.camera = cv2.VideoCapture(self.ip)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera')


    def get_frame(self):
        '''获取当前时刻的帧'''
        _, img = self.camera.read()
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        return frame

    def has_opened(self):
        '''判断摄像头是否正常工作'''
        return self.camera is not None and self.camera.isOpened()