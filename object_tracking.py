# -*- coding:utf-8 -*-
#!/usr/bin/env python

import cv2,argparse,sys,imutils
import numpy as np
from copy import deepcopy
from .object_detection import object_detector

class object_tracker:

	def __init__(self,predictor):
		#图像物体识别器
		self.predictor=predictor
		#物体跟踪器
		self.trackers=dict()
		#每一次识别的物体列表
		self.objects_detected=dict()


	'''
	对追踪器进行初始化，加入KCF跟踪器
	param frame：图像
	param threshold:阈值
	'''
	def preprocess(self,frame,threshold):
		out=self.predictor.predict(frame)
		objects_detected=self.predictor.operate_out(frame,out,threshold)

		objects_list=list(objects_detected.keys())

		print('Tracking the following objects',objects_list)

		if len(objects_list)>0:
			self.trackers={key:cv2.TrackerKCF_create() for key in objects_list}
			for item in objects_list:
				self.trackers[item].init(frame,objects_detected[item][0])

		self.objects_detected=objects_detected
		return

	'''
	对每一帧中的物体进行追踪
	param frame：图像
	param threshold:阈值,默认为0.35
	param update:是否更新跟踪物体，布尔值
	return frame:处理之后的图片
	'''
	def track(self,frame,update=False,threshold=0.35):
		if len(self.trackers)==0 or update:#进行初始化操作
			self.preprocess(frame,threshold)

		if len(self.objects_detected)>0:
			del_items=[]
			for obj,tracker in self.trackers.items():
				ok,bbox=tracker.update(frame)
				if ok:
					self.objects_detected[obj][0]=bbox
				else:
					print('Failed to track',obj)
					del_items.append(obj)

			for item in del_items:
				self.trackers.pop(item)
				self.objects_detected.pop(item)

		if len(self.objects_detected)>0:
			self.predictor.operate_frame(frame,self.objects_detected)

		else:
			cv2.putText(frame, 'Tracking Failure. Trying to detect more objects', (50,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
			self.preprocess(frame,threshold)

		return frame


if __name__=='__main__':
	cap=cv2.VideoCapture(0)
	predictor=object_detector('object_detection_model/MobileNetSSD_deploy.caffemodel','object_detection_model/MobileNetSSD_deploy.prototxt','object_detection_model/MobileNet_classes.txt')
	object_track=object_tracker(predictor)
	while(True):
		_, img = cap.read()
		img=object_track.track(img,threshold=0.4)
		cv2.imshow('test',img)
		if cv2.waitKey(25) & 0xFF==ord('q'):
			cv2.destroyAllWindows()
			break
