import cv2, face_recognition

class Camera:
    '''IP 摄像头类'''
    def __init__(self, ip=None):
        self.camera = None
        if ip is not None:
            self.set_ip(ip)
        self._count = 0

        # 以下两行代码在罪犯数据库构建前使用
        self.my_image = face_recognition.load_image_file("Intelligent-monitoring-platform/image/myphoto.jpg")
        self.my_face_encoding = face_recognition.face_encodings(self.my_image)[0]


    def set_ip(self, ip):
        '''设置摄像头的ip地址'''
        self.ip = ip
        if ip == "0": #打开系统摄像头
            self.camera = cv2.VideoCapture(0)
        else:
            self.camera = cv2.VideoCapture(self.ip)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera')

    def get_frame(self, process=[], frequency=2):
        '''
        获取当前时刻的帧
        :param process: 一个列表，表示帧需要经过哪些处理
        :param frequency: 频率，表示经过多少帧进行一次处理
        :return:
        '''
        _, img = self.camera.read()

        if self._count % frequency == 0: #当前帧需要进行处理
            if 'face_recognition' in process:
                img = self.face_recognize(img)
            elif 'object_detection' in process:
                img = self.object_detect(img)
        self._count = (self._count+1) % frequency

        frame = cv2.imencode('.jpg', img)[1].tobytes()
        return frame

    def face_recognize(self, image):
        '''人脸识别处理'''
        known_face_encodings = [
            self.my_face_encoding
        ]

        known_face_names = [
            "Jiang"
        ]

        small_image = cv2.resize(image, (0,0), fx=0.25, fy=0.25)
        rgb_small_image = small_image[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_image)
        face_encodings = face_recognition.face_encodings(rgb_small_image, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

            cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return image

    def object_detect(self, image):
        return image

    def has_opened(self):
        '''判断摄像头是否正常工作'''
        return self.camera is not None and self.camera.isOpened()