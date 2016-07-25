# -*- coding:utf-8 -*-
__author__ = '东方鹗'


from . import db
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from .import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import hashlib, os


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)
    role = db.Column(db.Boolean, default=False)
    articles = db.relationship('Article', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise ArithmeticError('非明文密码，不可读。')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def is_admin(self):
        return self.role is True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def is_author(self):
        return Article.query.filter_by(author_id=self.id).first()

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    articles = db.relationship('Article', backref='cty', lazy='dynamic')

    def __repr__(self):
        return '<Name %r>' % self.name


class TagSpaces(db.Model):
    __tablename__ = 'tag_spaces'
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    tagged = db.relationship('TagSpaces',
                             foreign_keys=[TagSpaces.tag_id],
                             backref=db.backref('tagged', lazy='joined'),
                             lazy='dynamic',
                             cascade='all, delete-orphan')

    def __repr__(self):
        return '<Name %r>' % self.name


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    tags = db.relationship('TagSpaces',
                           foreign_keys=[TagSpaces.article_id],
                           backref=db.backref('tags', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    def tag(self, tag):
        if not self.is_tagging(tag):
            t = TagSpaces(tags=self, tagged=tag)
            db.session.add(t)

    def untag(self, tag):
        f = self.tags.filter_by(tag_id=tag.id).first()
        if f:
            db.session.delete(f)

    def is_tagging(self, tag):
        return self.tags.filter_by(tag_id=tag.id).first() is not None

    def author(self):
        return User.query.get(self.author_id)

    def category(self):
        return Category.query.get(self.category_id)

    @property
    def taggeds(self):
        return Tag.query.join(TagSpaces, TagSpaces.tag_id == Tag.id).filter(TagSpaces.article_id == self.id)

    @property
    def category_name(self):
        return Category.query.get(self.category_id).name

    @property
    def tags_name(self):
        tag_spaces = TagSpaces.query.filter_by(article_id=self.id)
        tags = []
        for tag_space in tag_spaces:
            ts = Tag.query.get(tag_space.tag_id)
            tags.append(ts.name)
        return ', '.join(tags)

    @property
    def thread_key(self):
        return hashlib.new(name='md5', string=str(self.id)).hexdigest()

    def __repr__(self):
        return '<Title %r>' % self.title


class Plugin(db.Model):
    __tablename__ = 'plugins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    token = db.Column(db.String(128), index=True)
    status = db.Column(db.Boolean, default=False)

    @staticmethod
    def insert_plugins():
        plugins = [u'微信', u'微博', u'多说', u'百度分析']
        for p in plugins:
            plugin = Plugin.query.filter_by(name=p).first()
            if plugin is None:
                plugin = Plugin(name=p)
            db.session.add(plugin)
        db.session.commit()

    def __repr__(self):
        return '<Name %r>' % self.name


class Finder(object):
    def __init__(self, path=None):
        self.path = path
        self.current_path = self.path.replace(current_app.config['IMAGES_FOLDER'], u'')
        self.query = self.folder() + self.image()

    def image(self):
        allowed_extensions = set(['.jpg', '.jpeg', '.png', '.gif', '.bmp'])
        files = os.listdir(self.path)
        return [{u'name': i.decode('utf-8'), u'type': u'image'} for i in files if os.path.isfile(os.path.join(self.path, i)) and
                os.path.splitext(i)[1] in allowed_extensions]

    def folder(self):
        files = os.listdir(self.path)

        return [{u'name': i.encode('utf-8'), u'type': u'folder'} for i in files if os.path.isdir(os.path.join(self.path, i))]
