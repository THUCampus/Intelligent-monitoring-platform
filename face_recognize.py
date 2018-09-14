import cv2, face_recognition, pickle
from .db import get_db

class face_recognize:
    def __init__(self):
        pass

    def face_recognize(self, image, repainting=True):
        '''
        对image进行人脸识别
        :param image: 待处理的图片
        :param repainting: 若为False,则采用上一次的处理方式
        :return: 处理后的图片
        '''
        ratio = 0.25
        small_image = cv2.resize(image, (0,0), fx=ratio, fy=ratio)
        rgb_small_image = small_image[:, :, ::-1]

        if repainting:
            self.face_locations = face_recognition.face_locations(rgb_small_image)
            self.face_encodings = face_recognition.face_encodings(rgb_small_image, self.face_locations)

            self.face_ids = []
            self.face_important = []
            for face_encoding in self.face_encodings:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.4)
                id = "Unknown"
                important = "C"
                if True in matches:
                    first_match_index = matches.index(True)
                    id = self.known_face_id[first_match_index]
                    important = "A" if self.know_face_important[first_match_index] else "B"

                self.face_ids.append(id)
                self.face_important.append(important)

        for (top, right, bottom, left), id, important in zip(self.face_locations, self.face_ids, self.face_important):
            top *= int(1.0/ratio)
            right *= int(1.0/ratio)
            bottom *= int(1.0/ratio)
            left *= int(1.0/ratio)

            if important == "A":
                color = (0,0,255)
            elif important == "B":
                color = (0,255,0)
            else:
                color = (255, 0, 0)

            cv2.rectangle(image, (left, top), (right, bottom), color, 2)

            cv2.rectangle(image, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, id, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return image

    def update_criminal_information(self):
        '''更新罪犯数据'''
        db = get_db()
        criminals = db.execute(
            'SELECT id, encoding, important FROM criminal ORDER BY rank'
        )
        self.known_face_id = []
        self.known_face_encodings = []
        self.know_face_important = []
        for criminal in criminals:
            self.known_face_id.append(criminal['id'])
            self.known_face_encodings.append(pickle.loads(criminal['encoding']))
            self.know_face_important.append(criminal['important'])