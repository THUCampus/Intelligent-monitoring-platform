import cv2,sys
from . import face_recognize
from . import object_detect

class Camera:
    '''IP 摄像头类'''
    def __init__(self, ip=None):
        self.camera = None
        if ip is not None:
            self.set_ip(ip)
        self._count = 0

        self.face_recognize = face_recognize.face_recognize()
        self.face_recognize.update_criminal_information() #更新罪犯信息

    def set_ip(self, ip):
        '''设置摄像头的ip地址'''
        self.ip = ip
        if ip == "0": #打开系统摄像头
            self.camera = cv2.VideoCapture(0)
        else:
            self.camera = cv2.VideoCapture(self.ip)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera')

    def get_frame(self, process={}):
        '''
        获取当前时刻的帧和发现的逃犯列表
        :param process: 一个词典，表示帧需要经过哪些处理，key为处理方式，value为处理频率
        :return:
        '''
        _, img = self.camera.read()
        criminal_ids = []
        if 'face_recognition' in process.keys():
            img = self.face_recognize.face_recognize(
                img, repainting=(self._count % process['face_recognition'] == 0)
            )
            for criminal_id in self.face_recognize.face_ids:
                if criminal_id != "Unknown":
                    criminal_ids.append(criminal_id)

        elif 'object_detection' in process.keys():
            img = self.object_detect(img) # 需要提供不同的painting方式
        self._count = (self._count + 1) % (sys.maxsize/2)

        frame = cv2.imencode('.jpg', img)[1].tobytes()
        return frame,criminal_ids

    def object_detect(self, image):
        image=object_detect.object_detect(image)
        return image

    def has_opened(self):
        '''判断摄像头是否正常工作'''
        return self.camera is not None and self.camera.isOpened()
