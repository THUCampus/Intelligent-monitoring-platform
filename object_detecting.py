# -*- coding:utf-8 -*-
#!/usr/bin/env python

from distutils.version import StrictVersion
import numpy as np
import six.moves.urllib as urllib
import tensorflow as tf
import sys,tarfile,zipfile,cv2,os
import matplotlib
matplotlib.use('Agg')

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

#将上层目录导入进来
sys.path.append("Intelligent-monitoring-platform/")
from object_detection.utils import ops as utils_ops

#要求tensorflow的版本要高于1.9.0
if StrictVersion(tf.__version__) < StrictVersion('1.9.0'):
    raise ImportError('Please upgrade your TensorFlow installation to v1.9.* or later!')

from object_detection.utils import label_map_util

#选择加载那个模型，默认为ssd
MODEL_NAME = 'ssd_mobilenet_v1_coco_2018_01_28'
MODEL_FILE = 'Intelligent-monitoring-platform/object_detection/'+MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

#存储模型的路径
PATH_TO_FROZEN_GRAPH = 'Intelligent-monitoring-platform/object_detection/'+MODEL_NAME + '/frozen_inference_graph.pb'

#匹配正确标签名的文件路径
PATH_TO_LABELS = os.path.join('Intelligent-monitoring-platform/object_detection/data', 'mscoco_label_map.pbtxt')

#识别物品种类数
NUM_CLASSES = 90

#下载模型（若已有模型可注释此处不进行下载）
'''opener = urllib.request.URLopener()
opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
tar_file = tarfile.open(MODEL_FILE)
for file in tar_file.getmembers():
    file_name = os.path.basename(file.name)
    if 'frozen_inference_graph.pb' in file_name:
        tar_file.extract(file, os.getcwd())'''

#建一个图，导入tensorflow模型
detection_graph = tf.Graph()
with detection_graph.as_default():
    sess=tf.Session()
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

#导入标签名
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

#将图像转为数组的函数
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

class object_detector:
    '''
    识别图像中的物体
	:param image:一张图片（即为视频一帧）
	:param threshold:阈值，默认为0.35
	:return objects_detected:其中的key是每一个框的名称，每一个value都是形如[(left,top,width,height),confidence]的列表
	'''
    def object_detect(self,image,threshold=0.35):
        with detection_graph.as_default():
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in ['num_detections', 'detection_boxes', 'detection_scores',
            'detection_classes', 'detection_masks']:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
            if 'detection_masks' in tensor_dict:
                #对一张图片进行处理
                detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(detection_masks, detection_boxes, image.shape[0], image.shape[1])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                tensor_dict['detection_masks'] = tf.expand_dims(detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            #喂入数据
            output_dict = sess.run(tensor_dict,
                            feed_dict={image_tensor: np.expand_dims(image,axis=0)})

            #将输出数据转换类型
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                                            'detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]

            s_boxes=output_dict['detection_boxes'][output_dict['detection_scores'] > threshold]
            s_classes = output_dict['detection_classes'][output_dict['detection_scores'] > threshold]
            s_scores=output_dict['detection_scores'][output_dict['detection_scores'] > threshold]
            width, height = image.shape[1],image.shape[0]
            objects_detected = {}
            for i in range(len(s_classes)):
                num=0
                label = str(category_index[s_classes[i]]['name'])
                label_with_num=str(label)+'_'+str(num)
                while True:#为同一类物体编号
                    if label_with_num not in objects_detected.keys():
                        break
                    label_with_num=str(label)+'_'+str(num)
                    num=num+1
                ymin = s_boxes[i][0]*height
                xmin = s_boxes[i][1]*width
                ymax = s_boxes[i][2]*height
                xmax = s_boxes[i][3]*width
                score = s_scores[i]

                objects_detected[label_with_num] = [(int(xmin),int(ymin),int(xmax-xmin),int(ymax-ymin)),score]

            return objects_detected

    '''
    根据分割情况对图像进行处理
    param image:图像
    param objects_detected:object_detect函数返回的字典
    param whether_track:判断是否为跟踪状态，从而改变label值。默认为False
    '''
    def operate_frame(self,frame,objects_detected,whether_track=False):

        for object_,info in objects_detected.items():
            box=info[0]
            confidence=info[1]
            if not whether_track:
                label='%s:%.2f'%(object_.split('_')[0],confidence)
            else:
                label='%s:%.2f'%(object_,confidence)
            p1=(int(box[0]),int(box[1]))
            p2=(int(box[0]+box[2]),int(box[1]+box[3]))
            cv2.rectangle(frame,p1,p2,(255,0,0),2)
            left=int(box[0])
            top=int(box[1])
            labelSize,baseLine=cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            top=max(top,labelSize[1])
            cv2.rectangle(frame, (left, top - labelSize[1]-baseLine), (left + labelSize[0], top), (255, 0, 0), cv2.FILLED)
            cv2.putText(frame, label, (left, top-baseLine), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255),1)


if __name__=='__main__':
    pass
