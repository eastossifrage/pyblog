# -*- coding:utf-8 -*-
__author__ = '东方鹗'


from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(label=u'记住我', default=False)
    submit = SubmitField(u'登 录')


class AddAdminForm(Form):
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 16, message=u'用户名长度要在1和16之间'),
                           Regexp(ur'^[\u4E00-\u9FFF]+$', flags=0, message=u'用户名必须为中文')])
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo(u'password2', message=u'密码必须一致！')])
    password2 = PasswordField(u'重输密码', validators=[DataRequired()])
    submit = SubmitField(u'注 册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被注册！')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册！')


class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo(u'password2', message=u'密码必须一致！')])
    password2 = PasswordField(u'重输密码', validators=[DataRequired()])
    submit = SubmitField(u'更新密码')


class AddUserForm(Form):
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64, message=u'姓名长度要在1和64之间'),
                       Regexp(ur'^[\u4E00-\u9FFF]+$', flags=0, message=u'用户名必须为中文')])
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    role = SelectField(u'权限', choices=[(u'True', u'管理员'), (u'False', u'一般用户') ])
    status = SelectField(u'状态', choices=[(u'True', u'正常'), (u'False', u'注销') ])
    submit = SubmitField(u'添加用户')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被注册！')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册！')


class DeleteUserForm(Form):
    user_id = StringField()


class EditUserForm(Form):
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64, message=u'姓名长度要在1和64之间'),
                       Regexp(ur'^[\u4E00-\u9FFF]+$', flags=0, message=u'用户名必须为中文')])
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    role = SelectField(u'权限', choices=[(u'True', u'管理员'), (u'False', u'一般用户') ])
    status = SelectField(u'状态', choices=[(u'True', u'正常'), (u'False', u'注销')])
    submit = SubmitField(u'修改用户')


class WriteArticleForm(Form):
    title = StringField(u'标题')
    body = TextAreaField(u'文章内容')
    category = StringField(u'分类')
    tags = StringField(u'标签')
    submit = SubmitField(u'提交')


class EditArticleForm(Form):
    title = StringField(u'标题')
    body = TextAreaField(u'文章内容')
    category_name = StringField(u'分类')
    tags_name = StringField(u'标签')
    submit = SubmitField(u'提交')


class DeleteArticleForm(Form):
    article_id = StringField()


class BaidutongjiForm(Form):
    token = StringField(u'健值')
    status = SelectField(u'状态', choices=[(u'True', u'启用'), (u'False', u'停用')])
    submit = SubmitField(u'提交')


class AddFolderFOrm(Form):
    directory = StringField(u'文件夹')
    submit = SubmitField(u'确定')
