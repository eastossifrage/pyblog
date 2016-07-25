# -*- coding:utf-8 -*-
__author__ = '东方鹗'

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class SearchForm(Form):
	search = StringField('search', validators=[DataRequired()])

