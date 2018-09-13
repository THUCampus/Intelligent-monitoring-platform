from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .db import get_db,get_db_by_config
from .auth import login_required
from datetime import datetime
from blinker import signal
import json
import _thread

records_updated_signal = signal("update records")#警示记录发生更新的信号


def produce_record(db,item,item_id,user_id,camera_id):
    '''
    生成一条警示记录
    :param db: 传入的数据库
    :param item: 识别的物体
    :param item_id: 识别物体的编号
    :param user_id: 摄像头所属用户id
    :param camera_id: 相机id
    :return:
    '''
    same_item=db.execute(
        'SELECT * FROM intruding_records WHERE item = ? AND item_id = ? AND leave_time = ?',
        (item,item_id,'STILL IN')
    ).fetchone()

    if same_item is None:
        db.execute(
            'INSERT INTO intruding_records(enter_time,item,item_id,user_id,camera_id)'
            'VALUES (?,?,?,?,?)',
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),item,item_id,user_id,camera_id)
        )
        db.commit()
        records_updated_signal.send(user_id)#发送信号，表示用户usre_id的警示记录发生了更新
    else:
        return

def add_leave_time(db,item,item_id):
    '''
    加入物体离开时间
    :param db: 传入的数据库
    :param item: 识别的物体
    :param item_id: 识别物体的编号
    :return:
    '''
    same_item=db.execute(
        'SELECT * FROM intruding_records WHERE item = ? AND item_id = ? AND leave_time = ?',
        (item,item_id,'STILL IN')
    ).fetchone()

    if same_item is None:
        return
    else:
        db.execute(
            'UPDATE intruding_records SET leave_time = ? WHERE id = ?',
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),same_item['id'])
        )
        db.commit()
        records_updated_signal.send(same_item['user_id'])#发送信号，表示用户usre_id的警示记录发生了更新

def get_instruding_records(db,user_id):
    '''获取用户user_id的所有历史记录'''
    records = db.execute(
        'SELECT i.id, u.username as user_name, i.item as item,i.item_id as item_id,'
        'i.enter_time as enter_time,i.leave_time as leave_time,'
        'i.camera_id as camera_id FROM user u, intruding_records i '
        'WHERE i.user_id = u.id and u.id = ?'
        'ORDER BY i.enter_time DESC ',
        (user_id,)
    )
    return records

def _create_json_response(records):
    '''将records进行json序列化'''
    new_records = []
    for record in records:
        new_record={
            'item':record['item'],
            'item_id':record['item_id'],
            'enter_time': record['enter_time'],
            'leave_time': record['leave_time'],
            'camera_id': record['camera_id'],
            'id': record['id'],
        }
        new_records.append(new_record)
    return json.dumps(new_records)

class RecordsGenerator:
    '''物体进入记录生成器'''
    def __init__(self, user_id, db_config,whether_update=False):
        self.user_id = user_id
        self.db_config = db_config
        records_updated_signal.connect(self.on_records_update)
        self.lock = _thread.allocate_lock()
        if whether_update:
            #清空表数据
            db = get_db_by_config(config=self.db_config)
            db.execute('DELETE FROM intruding_records')
            db.commit()

    def on_records_update(self, user_id):
        '''当物体进入记录更新时'''
        if user_id == self.user_id:
            self.lock.release()

    def __iter__(self):
        while True:
            self.lock.acquire()  #只有当物体进入记录发生更新时，才会向客户端推送消息
            db = get_db_by_config(config=self.db_config)
            records = get_instruding_records(db, self.user_id).fetchmany(5)
            records = _create_json_response(records)
            yield "data: " + records + "\n\n"
