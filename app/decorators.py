# -*- coding:utf-8 -*-
__author__ = u'东方鹗'


from flask import abort
from threading import Thread
from functools import wraps
from flask_login import current_user
import os


def async(f):
    """ 多线程修饰器 """
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def admin_required(func):
    """ 检查管理员权限 """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin():
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator(func)


def author_required(func):
    """ 检查作者权限 """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_author():
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator(func)


def tag_split(tags):
    """
    :param tags: 输入要分隔的tags
    :return: 一个tags的List列表
    """
    ts = []
    for tag in tags.split(u','):
        t = tag.split(u'，')
        ts.extend(t)
    return ts




