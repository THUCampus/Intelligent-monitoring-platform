# -*- coding:utf-8 -*-
#!/usr/bin/env python

import cv2,argparse,sys,imutils,copy
import numpy as np
from copy import deepcopy
from .object_detecting import object_detector

class object_tracker:

	def __init__(self,predictor):
		#图像物体识别器
		self.predictor=predictor
		#物体跟踪器
		self.trackers=dict()
		#每一次识别的物体列表
		self.objects_detected=dict()
		#刷新频率
		self.freq=0
		#记录区域内的物体
		self.items_label=[]

	'''
	对追踪器进行初始化，加入KCF跟踪器
	param frame：图像
	param threshold:阈值
	'''
	def preprocess(self,frame,threshold):
		objects_detected=self.predictor.object_detect(frame,threshold)

		objects_list=list(objects_detected.keys())

		if len(objects_list)>0:
			self.trackers={key:cv2.TrackerKCF_create() for key in objects_list}
			for item in objects_list:
				self.trackers[item].init(frame,objects_detected[item][0])

		return objects_detected

	'''
	判断两个矩形的重叠百分比
	param box1,box2:两个矩形区域
	return coincide:重叠百分比
	'''
	def coincide(self,box1,box2):
		x01,y01,x02,y02=box1[0],box1[1],box1[0]+box1[2],box1[1]+box1[3]
		x11,y11,x12,y12=box2[0],box2[1],box2[0]+box2[2],box2[1]+box2[3]

		lx = abs((x01 + x02) / 2 - (x11 + x12) / 2)
		ly = abs((y01 + y02) / 2 - (y11 + y12) / 2)
		sax = abs(x01 - x02)
		sbx = abs(x11 - x12)
		say = abs(y01 - y02)
		sby = abs(y11 - y12)
		if lx <= (sax + sbx) / 2 and ly <= (say + sby) / 2:
			col=min(x02,x12)-max(x01,x11)
			row=min(y02,y12)-max(y01,y11)
			intersection=col*row
			area1=(x02-x01)*(y02-y01)
			area2=(x12-x11)*(y12-y11)
			coincide=intersection/(area1+area2-intersection)
			return coincide
		else:
			return 0

	'''
	判断是否有需要新加入的物体
	param frame：图像
	param threshold:阈值,默认为0.35
	return frame:处理之后的图片
	'''
	def add_new_object(self,frame,threshold):
		objects_detected=self.predictor.object_detect(frame,threshold)
		if(len(objects_detected)<=len(self.objects_detected)):
			#不加入新物体
			return
		else:
			#存储出现过的某label个数的字典
			label_num={}
			new_label_coincides={}
			label_pairs={}
			del_items=[]
			for old_label in self.objects_detected.keys():
				label,num=old_label.split('_')
				if label not in label_num.keys():
					label_num[label]=0
				else:
					label_num[label]=max(label_num[label],int(num)+1)
				for new_label in objects_detected.keys():
					if new_label not in new_label_coincides.keys():
						new_label_coincides[new_label]={}
					if label==new_label.split('_')[0]:
						new_label_coincides[new_label][old_label]=self.coincide(self.objects_detected[old_label][0],objects_detected[new_label][0])

			for new_label in new_label_coincides.keys():
				max_coincide=0
				label=''
				for old_label in new_label_coincides[new_label].keys():
					if new_label_coincides[new_label][old_label]>max_coincide:
						label=old_label
						max_coincide=new_label_coincides[new_label][old_label]
				if max_coincide>0.7 and label!='' and label not in label_pairs.keys():
					label_pairs[label]=new_label

			#更新保留的old_label，否则去除
			for old_label in self.objects_detected.keys():
				if old_label not in label_pairs.keys():
					del_items.append(old_label)
				else:
					self.trackers.pop(old_label)
					self.trackers[old_label]=cv2.TrackerKCF_create()
					self.trackers[old_label].init(frame,objects_detected[label_pairs[old_label]][0])
					objects_detected.pop(label_pairs[old_label])


			for old_label in del_items:
				self.trackers.pop(old_label)
				self.objects_detected.pop(old_label)
				if label_num[old_label.split('_')[0]]==int(old_label.split('_')[1])+1:
					label_num[old_label.split('_')[0]]=label_num[old_label.split('_')[0]]-1

			for remain_label in objects_detected.keys():#加入新物体
				label,num=remain_label.split('_')
				new_label=remain_label
				if label in label_num.keys():
					num=label_num[label]
					label_num[label]=label_num[label]+1
					new_label=label+'_'+str(num)
				self.objects_detected[new_label]=copy.deepcopy(objects_detected[remain_label])
				self.trackers[new_label]=cv2.TrackerKCF_create()
				self.trackers[new_label].init(frame,self.objects_detected[new_label][0])


	'''
	对每一帧中的物体进行追踪
	param frame：图像
	param box_selection:选择的监视区域，默认为[0,0,0,0]
	param threshold:阈值,默认为0.35
	return frame，enter_items_label，leave_items_label:
		处理之后的图片，进入监测区域中的物体，离开监测区域的物体
	'''
	def track(self,frame,box_selection=[0,0,0,0],threshold=0.35):
		if len(self.trackers)==0:#进行初始化操作
			self.objects_detected=self.preprocess(frame,threshold)

		if len(self.objects_detected)>0:
			del_items=[]
			for obj,tracker in self.trackers.items():
				ok,bbox=tracker.update(frame)
				if ok:
					self.objects_detected[obj][0]=bbox
				else:
					del_items.append(obj)

			for item in del_items:
				self.trackers.pop(item)
				self.objects_detected.pop(item)

		#进行加入新物体的更新
		self.freq=self.freq+1
		if(self.freq>=10):
			self.freq=0
			self.add_new_object(frame,threshold)

		#检测是否有物体进入指定区域
		enter_items_label=[]
		leave_items_label=[]
		if box_selection != [0,0,0,0]:
			p1=(int(box_selection[0]),int(box_selection[1]))
			p2=(int(box_selection[0]+box_selection[2]),int(box_selection[1]+box_selection[3]))
			cv2.rectangle(frame,p1,p2,(0,255,0),3)
			for label in self.objects_detected.keys():
				if self.coincide(self.objects_detected[label][0],box_selection)>0.01:
					enter_items_label.append(label)
			#和之前的记录对比
			for label in self.items_label:
				if label not in enter_items_label:
					leave_items_label.append(label)
			self.items_label=enter_items_label



		if len(self.objects_detected)>0:
			self.predictor.operate_frame(frame,self.objects_detected,whether_track=True)

		else:
			cv2.putText(frame, 'No objects to be tracked!', (50,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
			self.objects_detected=self.preprocess(frame,threshold)

		return frame,enter_items_label,leave_items_label


if __name__=='__main__':
	cap=cv2.VideoCapture(0)
	predictor=object_detector('object_detection_model/MobileNetSSD_deploy.caffemodel',
		'object_detection_model/MobileNetSSD_deploy.prototxt',
		'object_detection_model/MobileNet_classes.txt')
	object_track=object_tracker(predictor)
	while(True):
		_, img = cap.read()
		img=object_track.track(img,0.5)
		cv2.imshow('test',img)
		if cv2.waitKey(25) & 0xFF==ord('q'):
			cv2.destroyAllWindows()
			break
