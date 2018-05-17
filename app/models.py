# -*- coding:utf-8 -*-
__author__ = '东方鹗'


from . import db
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from .import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import hashlib, os
from ._customs import MyRenderer, KaTeXInlineLexer, MyMarkdown


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
        return self.role

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
    body_html = db.Column(db.Text)
    body_toc = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    tags = db.relationship('TagSpaces',
                           foreign_keys=[TagSpaces.article_id],
                           backref=db.backref('tags', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    def markdown_to_html(self, md):
        # --------以下功能是 Markdown 转换 html
        renderer = MyRenderer()
        inline = KaTeXInlineLexer(renderer=renderer)
        # block = KaTeXBlockLexer()
        # markdown = MyMarkdown(renderer=renderer, inline=inline, block=block)
        # 为更适应 editor.md 的科学公式块的显示模式，除非有必要，此处不再设置块形式代码。
        markdown = MyMarkdown(renderer=renderer, inline=inline)
        '''       
        # 请严格按照如下顺序书写代码
        toc.reset_toc()          # initial the status
        md.parse(text)           # parse for headers
        toc.render_toc(level=3)  # render TOC HTML
        '''
        renderer.reset_toc()
        self.body_html = markdown.parse(md)  # 不能再使用markdown(md)
        self.body_toc = renderer.render_toc(level=5)

    def tag(self, tag):
        """添加标识"""
        if not self.is_tagging(tag):
            t = TagSpaces(tags=self, tagged=tag)
            db.session.add(t)

    def untag(self, tag):
        """删除标识"""
        f = self.tags.filter_by(tag_id=tag.id).first()
        if f:
            db.session.delete(f)

    def is_tagging(self, tag):
        """判断该文章与标识是否关联"""
        return self.tags.filter_by(tag_id=tag.id).first() is not None

    @property
    def taggeds(self):
        """返回该文章所关联的标识对象"""
        return Tag.query.join(TagSpaces, TagSpaces.tag_id == Tag.id).filter(TagSpaces.article_id == self.id)

    @property
    def author(self):
        """返回作者对象"""
        return User.query.get(self.author_id)

    @property
    def category(self):
        """返回文章分类对象"""
        return Category.query.get(self.category_id)

    @property
    def category_name(self):
        """返回文章分类名称，主要是为了使用 flask-wtf 的 obj 返回对象的功能"""
        return Category.query.get(self.category_id).name

    @property
    def previous(self):
        """用于分页显示的上一页"""
        pre_id = self.id - 1

        return self.query.get(pre_id)

    @property
    def next(self):
        """用于分页显示的下一页"""
        next_id = self.id + 1

        return self.query.get(next_id)

    @property
    def tags_name(self):
        """返回文章的标签的字符串，用英文‘, ’分隔，主要用于修改文章功能"""
        tag_spaces = TagSpaces.query.filter_by(article_id=self.id)
        tags = []
        for tag_space in tag_spaces:
            ts = Tag.query.get(tag_space.tag_id)
            tags.append(ts.name)
        return ', '.join(tags)

    @property
    def thread_key(self): # 用于评论插件
        return hashlib.new(name='md5', string=str(self.id)).hexdigest()

    def __repr__(self):
        return '<Title %r>' % self.title


class Finder(object):
    def __init__(self, path=None):
        self.path = path
        self.current_path = self.path.replace(current_app.config['IMAGES_FOLDER'], u'')
        self.query = self.folder() + self.image()

    def image(self):
        allowed_extensions = set(['.jpg', '.jpeg', '.png', '.gif', '.bmp'])
        files = os.listdir(self.path)
        return [{'name': i, 'type': 'image'} for i in files
                if os.path.isfile(os.path.join(self.path, i)) and
                os.path.splitext(i)[1] in allowed_extensions]

    def folder(self):
        files = os.listdir(self.path)

        return [{'name': i, 'type': 'folder'} for i in files
                if os.path.isdir(os.path.join(self.path, i))]
