# -*- coding:utf-8 -*-
__author__ = '东方鹗'

from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import admin
from ..import db
from .forms import AddAdminForm, LoginForm, AddUserForm, DeleteUserForm, EditUserForm, WriteArticleForm, \
    EditArticleForm, DeleteArticleForm, ChangePasswordForm, AddFolderForm
from ..models import User, Category, Tag, Article, Finder
from ..decorators import admin_required, author_required, tag_split
import os
from werkzeug.utils import secure_filename
from datetime import datetime


@admin.route('/', methods=['GET', 'POST'])
@login_required
def index():
    current_user.ping()

    return render_template('admin/index.html')


@admin.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(prefix='login')
    user = User.query.filter_by(status=True).first()
    if not user:
        add_admin_form = AddAdminForm(prefix='add_admin')
        if add_admin_form.validate_on_submit():
            u = User(username=add_admin_form.username.data.strip(),
                     email=add_admin_form.email.data.strip(),
                     password=add_admin_form.password.data.strip(),
                     status=True, role=True
                     )
            db.session.add(u)
            db.session.commit()
            login_user(user=u)
            return redirect(url_for('admin.index'))

        return render_template('admin/add_admin.html', addAdminForm=add_admin_form)
    else:
        if login_form.validate_on_submit():
            u = User.query.filter_by(email=login_form.email.data.strip()).first()
            if u is None:
                flash({'error': '邮箱未注册！'})
            elif u is not None and u.verify_password(login_form.password.data.strip()) and u.status:
                login_user(user=u, remember=login_form.remember_me.data)
                return redirect(url_for('admin.index'))
            elif not u.status:
                flash({'error': '用户已被管理员注销！'})
            elif not u.verify_password(login_form.password.data.strip()):
                flash({'error': '密码不正确！'})

    return render_template('admin/login.html', loginForm=login_form)

@admin.route('/article-settings', methods=['GET', 'POST'])
@login_required
def article_settings():
    delete_article_form = DeleteArticleForm(prefix='delete_article')
    if delete_article_form.validate_on_submit():
        article = Article.query.get(int(delete_article_form.article_id.data))
        db.session.delete(article)

    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.timestamp.desc()).paginate(page, per_page=current_app.config['OUSI_POSTS_PER_PAGE'], error_out=False)

    return render_template('admin/articles.html', articles=articles, deleteArticleForm=delete_article_form)


@admin.route('/article_edit/<article_id>', methods=['GET', 'POST'])
@login_required
@author_required
def article_edit(article_id):
    article = Article.query.get(int(article_id))
    edit_article_form = EditArticleForm(prefix='edit_article', obj=article)
    if edit_article_form.validate_on_submit():
        # --------以下功能是修改文章的分类
        cty = Category.query.filter_by(name=edit_article_form.category_name.data.strip()).first()
        if not cty and edit_article_form.category.data.strip() != '':
            cty = Category(name=edit_article_form.category_name.data.strip())
            db.session.add(cty)
            article.cty = cty
        article.title = edit_article_form.title.data
        article.body = edit_article_form.body.data
        # ---- 修改文章的分类---结束

        # --------以下功能是 Markdown 转换 html
        article.markdown_to_html(edit_article_form.body.data)
        # -------- Markdown 转换 html ----结束

        # --------以下功能是删除旧有文章标签
        for tag in article.taggeds:
            article.untag(tag=tag)
        # --------删除旧有文章标签 --- 结束

        # --------以下功能是修改文章标识
        for tg in tag_split(tags=edit_article_form.tags_name.data):
            t = Tag.query.filter_by(name=tg.strip()).first()
            if not t:
                t = Tag(name=tg.strip())
                db.session.add(t)
            if not article.is_tagging(tag=t):
                article.tag(tag=t)
        # ----- 修改文章标识功能---结束

        return redirect(url_for('admin.article_settings'))

    return render_template('admin/edit_article.html', editArticleForm=edit_article_form)


@admin.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    write_article_form = WriteArticleForm(prefix='write')
    if write_article_form.validate_on_submit():
        # --------以下功能是增加文章的分类
        cty = Category.query.filter_by(name=write_article_form.category.data.strip()).first()
        if not cty and write_article_form.category.data.strip() != '':
            cty = Category(name=write_article_form.category.data.strip())
            db.session.add(cty)
        # --------增文章分类------结束

        # --------以下功能是将文章信息插入数据库
        a = Article(title=write_article_form.title.data.strip(), body=write_article_form.body.data,
                    cty=cty, author=current_user._get_current_object())
        db.session.add(a)

        # --------以下功能是 Markdown 转换 html
        a.markdown_to_html(write_article_form.body.data)
        # -------- Markdown 转换 html ----结束

        # --------以下功能是将文章标识插入数据库
        for tg in tag_split(tags=write_article_form.tags.data):
            t = Tag.query.filter_by(name=tg.strip()).first()
            if not t:
                t = Tag(name=tg.strip())
                db.session.add(t)
            a.tag(tag=t)
        # --------将文章标识插入数据库---结束
        return redirect(url_for('admin.article_settings'))
    directory = Finder(path=current_app.config['IMAGES_FOLDER'])

    return render_template('admin/write.html', writeArticleForm=write_article_form, directory=directory)


@admin.route('/user-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def user_settings():
    add_user_form = AddUserForm(prefix='add_user')
    delete_user_form = DeleteUserForm(prefix='delete_user')
    if add_user_form.validate_on_submit():
        if add_user_form.role.data == 'True':
            role = True
        else:
            role = False
        if add_user_form.status.data == 'True':
            status = True
        else:
            status = False
        u = User(username=add_user_form.username.data.strip(), email=add_user_form.email.data.strip(),
                 role=role, status=status, password='123456')
        db.session.add(u)
        flash({'success': '添加用户<%s>成功！' % add_user_form.username.data.strip()})
    if delete_user_form.validate_on_submit():
        u = User.query.get_or_404(int(delete_user_form.user_id.data.strip()))
        db.session.delete(u)
        flash({'success': '删除用户<%s>成功！' % u.username})

    users = User.query.all()

    return render_template('admin/users.html', users=users, addUserForm=add_user_form,
                           deleteUserForm=delete_user_form)


@admin.route('/user-edit/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    edit_user_form = EditUserForm(prefix='edit_user', obj=user)
    if edit_user_form.validate_on_submit():
        user.username = edit_user_form.username.data.strip()
        user.email = edit_user_form.email.data.strip()
        if edit_user_form.role.data == 'True':
            user.role = True
        else:
            user.role = False
        if edit_user_form.status.data == 'True':
            user.status = True
        else:
            user.status = False
        flash({'success': '用户资料已修改成功！'})

    return render_template('admin/edit_user.html', editUserForm=edit_user_form, user=user)


@admin.route('/password', methods=['GET', 'POST'])
@login_required
@admin_required
def password():
    change_password_form = ChangePasswordForm(prefix='change_password')
    if change_password_form.validate_on_submit():
        if current_user.verify_password(change_password_form.old_password.data.strip()):
            current_user.password = change_password_form.password.data.strip()
            # db.session.add(current_user)
            db.session.commit()
            flash({'success': '您的账户密码已修改成功！'})
        else:
            flash({'error': '无效的旧密码！'})

    return render_template('admin/password.html', changePasswordForm=change_password_form)


def allowed_file(filename, filetype):
    return '.' in filename and filename.rsplit('.', 1)[1] in filetype


@admin.route('/upload',methods=['POST'])
def upload():
    """图片上传处理"""
    file=request.files.get('editormd-image-file')
    if not file:
        res={
            'success':0,
            'message':'图片格式异常'
        }
    else:
        ex=os.path.splitext(file.filename)[1]
        filename=datetime.now().strftime('%Y%m%d%H%M%S')+ex
        file.save(os.path.join(current_app.config['IMAGES_FOLDER'],filename))
        #返回
        res={
            'success':1,
            'message':u'图片上传成功',
            'url':url_for('.static',filename='pictures/{}'.format(filename))
        }
    return jsonify(res)


@admin.route('/finder/<path>', methods=['GET', 'POST'])
@login_required
def finder(path):
    if not path == 'basedir':
        current_directory = os.path.join(current_app.config['IMAGES_FOLDER'], path)
    else:
        current_directory = current_app.config['IMAGES_FOLDER']

    add_folder_form = AddFolderForm(prefix='add_folder')
    if add_folder_form.validate_on_submit():
        os.chdir(current_directory)
        os.mkdir(add_folder_form.directory.data.strip())

    upload_files = request.files.getlist('file[]')
    for f in upload_files:
        if f and allowed_file(filename=f.filename, filetype=['jpg', 'jpeg', 'png', 'gif', 'bmp']):
            filename = secure_filename(f.filename)
            f.save(os.path.join(current_directory, filename))

    directory = Finder(path=current_directory)

    return render_template('admin/finder.html', directory=directory, addFolderForm=add_folder_form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

