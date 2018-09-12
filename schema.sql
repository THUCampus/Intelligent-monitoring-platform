DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS criminal;
DROP TABLE IF EXISTS history_records;
DROP TABLE IF EXISTS intruding_records;

CREATE TABLE user(--用户数据库
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL ,
  password TEXT NOT NULL,
  is_manager BOOLEAN NOT NULL
);

CREATE TABLE criminal(--逃犯信息数据库
  rank INTEGER PRIMARY KEY AUTOINCREMENT,--逃犯在数据库中的标识
  id TEXT NOT NULL UNIQUE,--逃犯的身份证号码
  name TEXT NOT NULL,--逃犯的名字
  encoding TEXT NOT NULL ,--逃犯的人脸编码
  important BOOLEAN DEFAULT FALSE--逃犯的犯罪等级
);

CREATE TABLE history_records(--历史警示记录
  id INTEGER PRIMARY KEY AUTOINCREMENT,--记录在数据库中的标识
  criminal_id TEXT NOT NULL,--逃犯的身份证号码
  time TIME NOT NULL,--记录发生的时间
  user_id INTEGER NOT NULL,--用户id
  camera_id TEXT NOT NULL,--相对于用户，摄像头的编号
  FOREIGN KEY (criminal_id) REFERENCES criminal(id), --逃犯的身份证号码
  FOREIGN KEY (user_id) REFERENCES user(id)--用户id
);

CREATE TABLE intruding_records(--有物体进入某区域的警示记录
  id INTEGER PRIMARY KEY AUTOINCREMENT,--记录在数据库中的标识
  enter_time TIME NOT NULL,--物体进入的时间
  leave_time TIME DEFAULT 'STILL IN',--物体离开的时间
  item TEXT NOT NULL,--什么物体进入
  item_id INTEGER NOT NULL,--进入物体的编号
  user_id INTEGER NOT NULL,--用户id
  camera_id TEXT NOT NULL,--相对于用户，摄像头的编号
  FOREIGN KEY (user_id) REFERENCES user(id)--用户id外键
);
