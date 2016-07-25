# -*- coding:utf-8 -*-
__author__ = '东方鹗'

import os
from app import create_app, db
from app.models import User, Category, Article, Tag, TagSpaces, Plugin
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app=app)
migrate = Migrate(app=app, db=db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Category=Category, Article=Article, Tag=Tag, TagSpaces=TagSpaces, Plugin=Plugin)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """ 单元测试 """
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(test=tests)

if __name__ == '__main__':
    manager.run()
