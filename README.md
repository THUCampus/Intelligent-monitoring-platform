# Intelligent monitoring platform

## 代码功能说明
网站服务采用了Flask开源框架，templates和static中分别存放了网页模板文件和静态文件。
- camera.py 中的Camera类实现从IP地址或者本地读取网络摄像头。
- db.py 中提供了数据库的创建、销毁、获取等操作。
- schema.sql 实现数据表的创建。
- auth.py 提供了网站中管理员和普通用户的登录、跳转等功能。
- video.py 实现了向前端推送视频和警示记录
- object_detecting.py中实现了用模型进行物体检测的功能。
- object_tracking.py中实现了用第三方库进行物体追踪的功能。
- face_recognize.py 实现对给定图像进行人脸识别（搜索罪犯）。
- criminal.py 提供了逃犯信息的录入、删除和查看。
- history_records.py 提供了嫌犯识别历史警示记录的生成、获取；通过信号机制连接数据库，通过生成器向前端推送警示信息。
- intruding_records.py 提供了物体进入选择区域警示记录的生成、获取；通过信号机制连接数据库，通过生成器向前端推送警示信息。
- records_management.py 提供了两种记录的删除操作。
- templates/中，base.html为基础界面，video.html为监控视频展示界面，history_records.html为完整的历史警示记录界面。
- templates/auth/中，login.html登录页面，manage.html管理界面，register.html注册界面，update_password.html修改密码界面
- templates/criminal/中，manage.html为逃犯的管理界面，register.html为逃犯信息录入界面
- object_detection/中是与物体检测相关的模型和类库。

## 部署说明
- 在目录Intelligent-monitoring-platform的上级目录打开命令行，输入(Mac或者Linux系统下)
```angular2html
export FLASK_APP=Intelligent-monitoring-platform
export FLASK_ENV=development
flask init-db
```
进行数据库的初始化，随后可以在Intelligent-monitoring-platform的同级目录中出现新的文件夹instance,其中存放了数据库内容。
然后输入
```angular2html
flask run
```
打开服务器，然后在网页输入localhost:5000/即可进入登录界面。
初始时数据库中有一个管理员用户，用户名为Boss, 密码为123456。

## 第三方库说明
我们用到的python第三方库包括flask,werkzeug,cv2,face_recognition,click,pickle,blinker,json,numpy,tensorflow,matplotlib，opencv-contrib-python

## 目前发现的一些bug
