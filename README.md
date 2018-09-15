## 作者：江俊广（JunguangJiang） 程嘉梁（JL-Cheng）
说明文档的网页版（格式更美观）见 [文档说明](https://shimo.im/docs/leUrk3mHdygyweDS)
# 代码架构
我们的智能监控平台的网站服务基于**Flask**开源框架，图像识别与信息提取功能则基于**cv2**和**tensorflow**等一系列相关的第三方库，具体的代码结构如下所示：
## python文件
* camera.py：Camera类实现从IP地址读取网络摄像头或者打开本地USB摄像头。
* db.py：提供了数据库的创建、销毁、获取等操作。
* auth.py：提供了网站中管理员和普通用户的登录、注册、修改密码等功能。
* video.py：向前端推送视频和警示记录。
* object_detecting.py：使用ssd_mobilenet模型进行物体检测。
* object_tracking.py：使用cv2的追踪器进行物体追踪。
* face_recognize.py：对给定图像进行人脸识别（搜索罪犯）。
* criminal.py：提供了逃犯信息的录入、删除和查看的功能。
* history_records.py：提供了嫌犯识别历史警示记录的生成、获取的功能；通过信号机制连接数据库，通过生成器向前端推送警示信息。
* intruding_records.py：提供了物体进入选择区域警示记录的生成、获取的功能；通过信号机制连接数据库，通过生成器向前端推送警示信息。
* records_management.py：提供了两种记录的删除操作。
## html模板文件
* templates/：base.html为基础界面模板，video.html为监控视频展示界面模板，history_records.html为完整的历史警示记录界面模板。
* templates/auth/：login.html为登录页面模板，manage.html为管理界面模板，register.html为注册界面模板，update_password.html为修改密码界面模板。
* templates/criminal/：manage.html为逃犯的管理界面模板，register.html为逃犯信息录入界面模板。
## 数据库文件
* schema.sql：创建数据表。
## 模型文件及相关类库
* object_detection/中是与物体检测相关的模型和类库。
# 部署方式（Mac/Linux/Windows）
## (Mac/Linux部署方式）
1. 在目录**Intelligent-monitoring-platform**的上级目录打开命令行，输入：
```
export FLASK_APP=Intelligent-monitoring-platform
export FLASK_ENV=development
flask init-db
```
此操作为数据库的初始化，随后可以在上级目录中看到一个新的文件夹instance,其中存放了与数据库相关的内容。
2. 在相同的目录下输入：
```
flask run
```
此时服务器已经打开。在服务器本机网页输入**localhost:5000/**即可进入登录界面。 初始时数据库中有一个管理员用户，**用户名**为Boss, **密码**为123456。
## (Windows部署方式）
1. 在目录**Intelligent-monitoring-platform**的上级目录打开命令行，输入：
```
set FLASK_APP=Intelligent-monitoring-platform
set FLASK_ENV=development
flask init-db
```
此操作为数据库的初始化，随后可以在上级目录中看到一个新的文件夹instance,其中存放了与数据库相关的内容
2. 在相同的目录下输入：
```
flask run
```
此时服务器已经打开。在服务器本机网页输入**localhost:5000/**即可进入登录界面。 初始时数据库中有一个管理员用户，**用户名**为Boss, **密码**为123456。
# 使用说明（包括运行时截图）
## 登录界面
![图片](https://images-cdn.shimo.im/5P21gcaJljMRcpmO/无标题.png!thumbnail)
* 输入**用户名**与**密码**即可登录。若用户名或密码有误，则会发出错误通知。
## 视频监控界面
![图片](https://images-cdn.shimo.im/iWeQkzhERRE3mThf/无标题.png!thumbnail)
* 该界面为监控系统主要界面。
* 右上角人像旁显示现在登录的**用户名**，右侧登**出按钮**可用于注销或切换用户。
* 标题下方的**四个页标签**可用于切换到各自功能的对应界面。
* 两个输入框为摄像头对应的**ip地址**和**ID**，点击提交按钮可切换到对应的摄像头。
* 下拉选择按钮可选择**三种监控方式**：**物体识别**、**物体跟踪与人脸识别**。
* 在**人脸识别界面****（下图），会将所有检测到的人脸分成三类，A级罪犯（红色），B级罪犯（绿色），普通人（蓝色），并标注罪犯的身份证号。此外，还提供了时间间隔提交框**，用于设置检测频率。

![图片](https://images-cdn.shimo.im/MF5N0LpxkPEtXnoT/屏幕快照_2018_09_14_下午8.12.27.png!thumbnail)
* 在**物体追踪界面**和**物体识别界面**有**阈值选择滑块**，可选择识别可信度的阈值。
* 在**物体追踪界面****（下图）**会显示所有被跟踪物体的类别和id。可用鼠标在视频画面内框选，选取要监视的区域，此后当被跟踪物体进入或者离开该区域时都会产生一条记录。

![图片](https://images-cdn.shimo.im/yusYCGmoJB4EpWwW/屏幕快照_2018_09_14_下午8.05.50.png!thumbnail)
* 视频右侧为**最新警示记录**，会显示数据库中最新的(至多)五条信息。
## 历史警示记录查看界面
![图片](https://images-cdn.shimo.im/iFN2Oj5OL1AWE8mE/无标题.png!thumbnail)
* 历史警示界面中有**两个可选标签**：**物体追踪记录**和**罪犯识别记录**。
* 每种记录均以列表形式显示，点击**删除按钮**可删掉对应的记录。
## 用户信息操作界面
![图片](https://images-cdn.shimo.im/1KcCwNlw0k8sSqCo/无标题.png!thumbnail)
点击**用户信息操作**的下拉标签，若为**管理员**则可看到**密码修改**、**用户注册**和**管理员界面**三个选项；若为**普通用户**则只能看到**密码修改**一个选项。
1. 密码修改界面

![图片](https://images-cdn.shimo.im/aGEa4yIC79YEq9Nm/无标题.png!thumbnail)
* 输入**用户名**、**旧密码**与**新密码**，点击**修改密码按钮**即可完成修改。若用户名或旧密码有误，则会发出错误通知。
2. 用户注册界面

![图片](https://images-cdn.shimo.im/R8P0UfVhkTwsRUi4/无标题.png!thumbnail)
* 输入**用户名**与**密码**，在**下拉按钮**中选择是否为管理员，点击**注册新用户按钮**即可完成注册。若用户名与已有用户名冲突冲突，则会发出错误通知。
3. 管理员界面

![图片](https://images-cdn.shimo.im/5PaxNaeyxEQQKLXL/无标题.png!thumbnail)
* 在**管理员界面**中会显示**已注册的用户记录**，若用户性质为管理员，则会在右上角显示**管理员标签**。点击**删除按钮**可删除对应用户（无法删除自身）。
## 罪犯信息操作界面
![图片](https://images-cdn.shimo.im/a256wrQYBkwDtJsh/无标题.png!thumbnail)
点击**罪犯信息操作**的下拉标签，若为**管理员**则可看到**罪犯信息录入**和**查看所有罪犯两**个选项；若为**普通用户**则只能看到**查看所有罪犯**一个选项。
1. 查看所有罪犯界面

![图片](https://images-cdn.shimo.im/udjrvP5glHwwoYu2/无标题.png!thumbnail)
* 在**查看所有罪犯界面**中会显示**已录入的罪犯信息，**在右上角显示**罪犯等级标签**。点击**删除按钮**可删除对应罪犯记录。
2. 罪犯信息录入界面

![图片](https://images-cdn.shimo.im/BY2HBE4i5tYoWYp2/无标题.png!thumbnail)
* 选择**对应照片**，输入**逃犯证件号**与**逃犯姓名**，选择**逃犯等级，**点击**上传按钮**即可录入逃犯记录。（**注：一定要是人脸照片，否则可能出错！**）
# 算法说明
## 网站服务搭建
我们采用**Flask框架**搭建了网站。权限分为“未登录”，“登录用户”，“管理员”三个等级。**对于不同等级有以下规则限制**：
* “未登录”状态下不能进行任何操作（即使直接通过url也不能进行任何操作）。
* “登录用户”可以进入“监控界面”，“查看所有的逃犯”，查看“历史警示记录”，“修改密码”。
* “管理员”拥有“登录用户”的所有权限，同时还能进入“管理员界面”对除了自身外的用户进行管理，“注册新用户”，录入“逃犯信息”等。

**具体实现方式如下**：
* 通过一个用户数据库user（schema.sql）记录所有用户的信息。字段包括用户名username和密码password的哈希码，当用户发出登录请求时，将登录信息中的密码哈希后与数据库中存储的哈希码进行比对校验用户，通过is_manager来区分权限。
* 每次登录后，会将登录状态记录在session中，这样用户在短期内重新打开同一个浏览器就不需要重新登录。
* 所有的路由响应函数都通过login_required（auth.py,需要登录权限）或者manager_required（auth.py,需要管理员权限）进行装饰。装饰器作用是通过对用户权限的判断，来判断是否需要对网页进行重定向。
## 摄像头画面的读取与显示
### 读取摄像头
摄像头（camera.py)同时支持系统摄像头和ip摄像头。
* 当输入ip为0时，切换到系统摄像头。
* 当输入为ip地址时，切换到ip摄像头（例如，采用ios系统下的IPCamera APP，模拟一个ip摄像头，此时的ip输入为“[http://admin:password@101.5.242.113:8081](http://admin:password@101.5.242.113:8081)” ）。
### 网页端显示监控画面
我们采用流媒体技术向前端推送视频流，具体实现方式（video.py)如下：
1. 生成器gen(video.py)不断的生成新的图像数据，将生成器作为Response中的参数返回。
2. 此后每当生成器产生新的数据时，就会有新的Response产生。
3. 同时，监控页面（video.html)中不断刷新的区域也仅仅局限在Response所对应的视频区域。
>参考资料： [https://blog.miguelgrinberg.com/post/video-streaming-with-flask](https://blog.miguelgrinberg.com/post/video-streaming-with-flask)
## 使用人工智能技术分析监控视频
我们实现了多种分析任务，用户可以通过在监控视频页面进行选择。
### 人脸识别（用于逃犯的搜捕）
1. 首先调用python的第三方库face_recognition，将所有逃犯的照片进行编码录入数据库criminal(schema.sql)中。
2. 然后对视频中人脸进行识别和编码，与数据库中编码进行比对。
3. 如果出现编码非常接近的，则判断该人为数据库中的对应逃犯。
4. 由于搜捕逃犯的任务特殊（把普通人错认成逃犯的代价比较大），因此在设置相关参数时，尽可能降低了匹配的概率，因此无法识别出逃犯的概率较大。但是只要在某一时刻发现了逃犯，系统就会留下记录。
### 物体识别
* 使用tensorflow加载已有的ssd_mobilenet模型，对图片进行物体检测。
### 物体跟踪
1. 使用物体识别中的模型进行物体检测与识别。
2. 使用opencv自带的opencv object tracker model中的KCF tracker进行物体跟踪。
3. 脚本会定期进行画面更新，通过新一轮的图片识别和位置比对，搜索新加入画面中的物体，并为它增加一个跟踪器。（但是最后测试结果不甚满意）。
## 提供监控警报功能
* 在人脸识别模式下，若出现了逃犯数据库中录入的人脸，则生成警报记录。用户可以在监控界面修改两次警示记录之间的最短间隔，默认为5分钟。（避免系统一直生成两条时间上非常接近的记录）
* 在物体追踪模式下，若有人进入划定区域，则生成警报记录。

同时我们也实现了基于主动推送显示最新的警示消息到网页上。具体原理类似于流媒体，简述如下：
1. 当警示记录数据库中的生成了一条新的警示记录时，会发出一个信号。
2. 记录生成器类的on_records_update方法会接受到这个信号，并释放一个锁资源。
3. 记录生成器的迭代方法__iter__内每获取一个锁资源，就会生成一个消息。
4. 将记录生成器作为Response的参数，从而实现向客户端主动推送消息。
# 项目中所用到的第三方库
* opencv-python<br>
维护者：Olli-Pekka Heinisuo、skvark<br>
协议：MIT License (MIT)<br>
开源<br>
使用到的功能：图片处理<br><br>
* imutils<br>
作者：Adrian RoseBrock<br>
协议：MIT License (MIT)<br>
开源<br>
使用到的功能：简单的图片处理<br><br>
* numpy<br>
作者：Travis E. Oliphant et al.<br>
协议：OSI Approved (BSD)<br>
开源<br>
使用到的功能：各种数学运算<br><br>
* opencv-contrib-python<br>
维护者：Olli-Pekka Heinisuo、skvark<br>
协议：MIT License (MIT)<br>
开源<br>
使用到的功能：opencv中的物体追踪器<br><br>
* six<br>
作者：Benjamin Peterson<br>
协议：MIT License (MIT)<br>
开源（托管在Bitbucket上）<br>
使用到的功能：兼容python2和python3的库<br><br>
* tensorflow<br>
作者：Google<br>
协议：Apache Software License (Apache 2.0)<br>
开源<br>
使用到的功能：对于深度学习模型的使用<br><br>
* matplotlib<br>
作者：John D. Hunter, Michael Droettboom<br>
协议：Python Software Foundation License (BSD)<br>
开源<br>
使用到的功能：图片处理与绘制操作<br><br>
* flask,werkzeug<br>
作者：Armin Ronacher, Pallets team<br>
协议：BSD<br>
开源<br>
使用到的功能：网站服务的搭建<br><br>
* face_recognition<br>
作者：Adam Geitgey<br>
协议：MIT License (MIT)<br>
开源<br>
使用到的功能：人脸识别<br><br>
* click<br>
作者：Armin Ronacher<br>
协议：BSD<br>
开源<br>
使用到的功能：命令行包装器<br><br>
* pickle<br>
作者：Antoine Pitrou<br>
协议：Python Software Foundation License<br>
开源<br>
使用到的功能：数据对象的持久化<br><br>
* blinker<br>
作者：Jason Kirtland<br>
协议：MIT License (MIT)<br>
开源<br>
使用到的功能：实现信号机制（警示记录发生更新时发出信号）<br><br>
