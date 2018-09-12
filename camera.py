import cv2,sys
from . import face_recognize
from . import object_detecting
from . import object_tracking

class Camera:
    '''IP 摄像头类'''
    def __init__(self, ip=None):
        self.camera = None
        if ip is not None:
            self.set_ip(ip)
        self._count = 0

        #加入物体识别对象和物体追踪对象
        self.object_predictor=object_detecting.object_detector()
        self.object_tracker=object_tracking.object_tracker(self.object_predictor)

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
        enter_items_label=[]#进入指定区域的物体标签名
        leave_items_label=[]#离开指定区域的物体标签名
        if 'face_recognition' in process.keys():
            img = self.face_recognize.face_recognize(
                img, repainting=(self._count % process['face_recognition'] == 0)
            )
            for criminal_id in self.face_recognize.face_ids:
                if criminal_id != "Unknown":
                    criminal_ids.append(criminal_id)
        elif 'object_detection' in process.keys():
            self.object_predictor.operate_frame(img,
                self.object_predictor.object_detect(img,0.6))

        elif 'object_track' in process.keys():
            img,enter_items_label,leave_items_label=self.object_tracker.track(img,box_selection=process['box'],threshold=0.6)
        self._count = (self._count + 1) % (sys.maxsize/2)

        frame = cv2.imencode('.jpg', img)[1].tobytes()
        return frame,criminal_ids,enter_items_label,leave_items_label

    def has_opened(self):
        '''判断摄像头是否正常工作'''
        return self.camera is not None and self.camera.isOpened()
