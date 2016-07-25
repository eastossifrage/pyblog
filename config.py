# -*- coding:utf-8 -*-
__author__ = u'东方鹗'

import os
import hashlib

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or hashlib.new(name='md5', string='ousi keji hawk@#').hexdigest()
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	OUSI_POSTS_PER_PAGE = 5
	THEMES_FOLDER = os.path.join(basedir, 'app/main/templates')
	IMAGES_FOLDER = os.path.join(basedir, 'app/admin/static/pictures')
	MAX_CONTENT_LENGTH = 32 * 1024 * 1024

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
							'sqlite:///' + os.path.join(basedir, 'data_dev.sqlite')


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
							'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
							'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}
