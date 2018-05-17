# -*- coding:utf-8 -*-
__author__ = '东方鹗'


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField(label='记住我', default=False)
    submit = SubmitField('登 录')


class AddAdminForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 16, message='用户名长度要在1和16之间'),
                           Regexp('^[\u4E00-\u9FFF]+$', flags=0, message='用户名必须为中文')])
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64, message='邮件长度要在6和64之间'),
                        Email(message='邮件格式不正确！')])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='密码必须一致！')])
    password2 = PasswordField('重输密码', validators=[DataRequired()])
    submit = SubmitField('注 册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册！')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册！')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='密码必须一致！')])
    password2 = PasswordField('重输密码', validators=[DataRequired()])
    submit = SubmitField('更新密码')


class AddUserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64, message='姓名长度要在1和64之间'),
                       Regexp('^[\u4E00-\u9FFF]+$', flags=0, message='用户名必须为中文')])
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64, message='邮件长度要在6和64之间'),
                        Email(message='邮件格式不正确！')])
    role = SelectField('权限', choices=[('True', '管理员'), ('False', '一般用户') ])
    status = SelectField('状态', choices=[('True', '正常'), ('False', '注销') ])
    submit = SubmitField('添加用户')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册！')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册！')


class DeleteUserForm(FlaskForm):
    user_id = StringField()


class EditUserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64, message='姓名长度要在1和64之间'),
                       Regexp('^[\u4E00-\u9FFF]+$', flags=0, message='用户名必须为中文')])
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64, message='邮件长度要在6和64之间'),
                        Email(message='邮件格式不正确！')])
    role = SelectField('权限', choices=[('True', '管理员'), ('False', '一般用户') ])
    status = SelectField('状态', choices=[('True', '正常'), ('False', '注销')])
    submit = SubmitField('修改用户')


class WriteArticleForm(FlaskForm):
    title = StringField('标题')
    body = TextAreaField('文章内容')
    category = StringField('分类')
    tags = StringField('标签')
    submit = SubmitField('提交')


class EditArticleForm(FlaskForm):
    title = StringField('标题')
    body = TextAreaField('文章内容')
    category_name = StringField('分类')
    tags_name = StringField('标签')
    submit = SubmitField('提交')


class DeleteArticleForm(FlaskForm):
    article_id = StringField()


class BaidutongjiForm(FlaskForm):
    token = StringField('健值')
    status = SelectField('状态', choices=[('True', '启用'), ('False', '停用')])
    submit = SubmitField('提交')


class AddFolderForm(FlaskForm):
    directory = StringField('文件夹')
    submit = SubmitField('确定')
