import sqlite3
import click
from flask import current_app,g
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash

def get_db():
    '''获取一个数据库连接'''
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def get_db_by_config(config):
    '''获取一个数据库连接'''
    db = sqlite3.connect(
        config,
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    return db


def close_db(e=None):
    '''关闭数据库连接'''
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    '''初始化数据库'''
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    '''Clear the existing data and create new tables'''
    init_db()
    click.echo("Initialized the database")

    db = get_db()
    db.execute(
        "INSERT INTO user (username, password, is_manager) VALUES (?, ?, ?)",
        ("Boss",  generate_password_hash("123456"), True)
    ) # 初始时数据库中有一个管理员用户，用户名为Boss, 密码为123456
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db) #关闭app时，需要关闭数据库连接
    app.cli.add_command(init_db_command)
