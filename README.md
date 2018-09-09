# Intelligent monitoring platform

## 代码功能说明
- 网站服务采用了Flask开源框架，templates和static中分别存放了网页模板文件和静态文件。
- camera.py 中的Camera类实现从IP地址读取网络摄像头。
- db.py 中提供了数据库的创建、销毁、获取等操作。
- auth.py 提供了网站中管理员和普通用户的登录、跳转等功能。
- video.py 实现了向前端推送视频。
- schema.sql 实现数据表的创建。
- templates/auth/中，login.html登录页面，manage.html管理界面，register.html注册界面，update_password.html修改密码界面
- templates/中，base.html为基础界面，video.html为监控视频展示界面。

## 部署说明
- 在目录Intelligent-monitoring-platform的上级目录打开命令行，输入
```angular2html
export FLASK_APP=Intelligent-monitoring-platform
export FLASK_ENV=development
flask init-db
```
进行数据库的初始化，随后可以在上级目录中看到一个新的文件夹instance,其中存放了数据库内容。
- 然后输入
```angular2html
flask run
```
打开服务器，然后在网页输入localhost:5000/即可进入登录界面。
初始时数据库中有一个管理员用户，用户名为Boss, 密码为123456。

## 网站服务功能
### 有待改进
- 监控视频自动调节到一个合适的大小进行显示

## 人工智能技术
### 分析目标
- 检测人脸，与逃犯数据库进行比对，帮助抓捕逃犯
- 检测行人位置,并加以追踪
- 对图像中出现的各种物体进行识别和分类