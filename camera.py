import cv2

class Camera:
    def __init__(self, ip=None):
        self.camera = None
        if ip:
            self.set_ip(ip)

    def set_ip(self, ip):
        '''设置摄像头的ip地址'''
        self.ip = ip
        self.camera = cv2.VideoCapture(self.ip)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera')

    def get_frame(self):
        _, img = self.camera.read()
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        return frame

    def has_opened(self):
        return self.camera is not None and self.camera.isOpened()