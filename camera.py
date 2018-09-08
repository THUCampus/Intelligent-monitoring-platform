import cv2

class Camera:
    '''IP 摄像头类'''
    def __init__(self, ip=None):
        self.camera = None
        if ip is not None:
            self.set_ip(ip)
        self._count = 0

    def set_ip(self, ip):
        '''设置摄像头的ip地址'''
        self.ip = ip
        if ip == "0": #打开系统摄像头
            self.camera = cv2.VideoCapture(0)
        else:
            self.camera = cv2.VideoCapture(self.ip)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera')

    def get_frame(self, process={}, frequency=2):
        '''
        获取当前时刻的帧
        :param process: 一个字典，表示帧需要经过哪些处理
        :param frequency: 频率，表示经过多少帧进行一次处理
        :return:
        '''
        _, img = self.camera.read()

        if self._count % frequency == 0: #当前帧需要进行处理
            if 'face_recognization' in process.keys():
                img = self.face_recognize(img)
            elif 'object_detection' in process.keys():
                img = self.object_detect(img)
        self._count = (self._count+1) % frequency

        frame = cv2.imencode('.jpg', img)[1].tobytes()
        return frame

    def face_recognize(self, image):
        return image

    def object_detect(self, image):
        return image

    def has_opened(self):
        '''判断摄像头是否正常工作'''
        return self.camera is not None and self.camera.isOpened()