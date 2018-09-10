# -*- coding:utf-8 -*-
#!/usr/bin/env python

import cv2
import sys
import numpy as np

class object_detector:

	def __init__(self,model,cfg,classes_file=""):
		self.model=model
		self.cfg=cfg
		self.framework=None

		if classes_file!="":
			with open(classes_file, 'rt') as f:
				self.classes = f.read().rstrip('\n').split('\n')
		else:
			self.classes = list(np.arange(0,100))

		self.load_model()

	'''
	加载模型
	'''
	def load_model(self):
		#判断加载的模型种类，根据对应后缀加载模型
		if self.model.endswith('weights') and self.cfg.endswith('cfg'):
			self.net=cv2.dnn.readNetFromDarknet(self.cfg,self.model)
			self.framework='Darknet'
		elif self.model.endswith('caffemodel') and self.cfg.endswith('prototxt'):
			self.net=cv2.dnn.readNetFromCaffe(self.cfg,self.model)
			self.framework='caffe'
		else:
			sys.exit('Wrong model!')
		self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
		self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

	'''
	进行图像物体分割
	param frame:输入图像
	'''
	def predict(self,frame):
		#从图像创建一个四维的二进制对象
		if self.framework=='Darknet':
			blob=cv2.dnn.blobFromImage(cv2.resize(frame,(416,416)),0.003921,(416,416),(0,0,0),swapRB=True,crop=False)
		else:
			blob=cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),0.007843,(300,300),127.5)

		#运行模型
		self.net.setInput(blob)
		out=self.net.forward()

		return out

	'''
	将图像分割返回的out数组进行处理，处理成一个dict存储各个框的属性
	param frame:图像
	param out:predict函数返回的数组
	param threshold:选择的阈值，默认为0.35
	return objects_detected:其中的key是每一个框的名称，每一个value都是形如[(left,top,width,height),confidence]的列表
	'''
	def operate_out(self,frame,out,threshold=0.35):
		frameHeight = frame.shape[0]
		frameWidth = frame.shape[1]
		objects_detected = dict()

		if self.framework=='caffe':
			for detection in out[0,0]:
				confidence=detection[2]#置信度
				if confidence>threshold:#置信度比阈值大就提取信息
					left=int(detection[3]*frameWidth)
					top=int(detection[4]*frameHeight)
					right=int(detection[5]*frameWidth)
					bottom=int(detection[6]*frameHeight)

					classId=int(detection[1])
					label=self.classes[classId]
					num=0
					label_with_num=str(label)+'_'+str(num)
					while True:#为同一类物体编号
						if label_with_num not in objects_detected.keys():
							break
						label_with_num=str(label)+'_'+str(num)
						num=num+1
					objects_detected[label_with_num] = [(int(left),int(top),int(right - left), int(bottom-top)),confidence]

		else:
			for detection in out:
				confidences=detection[5:]
				classId=np.argmax(confidences)
				confidence=confidences[classId]
				if confidence>threshold:#置信度比阈值大就提取信息
					center_x=int(detection[0]*frameWidth)
					center_y=int(detection[1]*frameHeight)
					width=int(detection[2]*frameWidth)
					height=int(detection[3]*frameHeight)
					left=center_x-(width/2)
					top=center_y-(height/2)

					num=0
					label=self.classes[classId]
					label_with_num=str(label)+'_'+str(num)
					while True:#为同一类物体编号
						if label_with_num not in objects_detected.keys():
							break
						label_with_num=str(label)+'_'+str(num)
						num=num+1
					objects_detected[label_with_num] = [(int(left),int(top),int(width),int(height)),confidence]

		return objects_detected

	'''
	根据分割情况对图像进行处理
	param frame:图像
	param objects_detected:operate_out函数返回的字典
	'''
	def operate_frame(self,frame,objects_detected):

		for object_,info in objects_detected.items():
			box=info[0]
			confidence=info[1]
			label='%s:%.2f'%(object_,confidence)
			p1=(int(box[0]),int(box[1]))
			p2=(int(box[0]+box[2]),int(box[1]+box[3]))
			cv2.rectangle(frame,p1,p2,(0,255,0))
			left=int(box[0])
			top=int(box[1])
			labelSize,baseLine=cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
			top=max(top,labelSize[1])
			cv2.rectangle(frame, (left, top - labelSize[1]), (left + labelSize[0], top + baseLine), (255, 255, 255), cv2.FILLED)
			cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))




if __name__=='__main__':
	cap=cv2.VideoCapture(0)
	object_predict=object_detector('object_detection_model/MobileNetSSD_deploy.caffemodel','object_detection_model/MobileNetSSD_deploy.prototxt','object_detection_model/MobileNet_classes.txt')
	while(True):
		_, img = cap.read()
		out=object_predict.predict(img)
		objects_detected=object_predict.operate_out(img,out,0.6)
		object_predict.operate_frame(img,objects_detected)
		cv2.imshow('test',img)
		if cv2.waitKey(25) & 0xFF==ord('q'):
			cv2.destroyAllWindows()
			break
