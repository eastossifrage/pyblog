# -*- coding:utf-8 -*-
__author__ = '东方鹗'

from flask import render_template, redirect, request, current_app, url_for, g
from . import main
from ..models import Article, Tag, Category, TagSpaces
from .forms import SearchForm


@main.before_request
def before_request():
    g.tags = Tag.query.all()
    g.categorys = Category.query.all()
    g.recent_articles = Article.query.order_by(Article.timestamp.desc()).limit(5).all()
    articles = Article.query.order_by(Article.timestamp.desc()).all()
    time_tag = []
    for a in articles:
        if a.timestamp.strftime('%Y-%m') not in time_tag:
            time_tag.append(a.timestamp.strftime('%Y-%m'))
    g.time_tag = time_tag
    g.search_form = SearchForm(prefix='search')


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['OUSI_POSTS_PER_PAGE'], error_out=False)

    return render_template('index.html', articles=articles)

@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@main.route('/article/<pid>', methods=['GET', 'POST'])
def article(pid):
    article = Article.query.get(int(pid))

    return render_template('article.html', article=article)


@main.route('/tag/<t>', methods=['GET', 'POST'])
def tag(t):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter_by(name=t).first()
    articles = Article.query.join(TagSpaces, TagSpaces.tag_id == tag.id).filter(TagSpaces.article_id == Article.id). \
        order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['OUSI_POSTS_PER_PAGE'], error_out=False)

    return render_template('tag.html', articles=articles, tag=tag)


@main.route('/category/<c>', methods=['GET', 'POST'])
def category(c):
    page = request.args.get('page', 1, type=int)
    cty = Category.query.filter_by(name=c).first()
    articles = Article.query.filter_by(cty=cty).order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['OUSI_POSTS_PER_PAGE'], error_out=False)

    return render_template('category.html', articles=articles, category=cty)


@main.route('/archives/<time_tag>', methods=['GET', 'POST'])
def archives(time_tag):
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter(Article.timestamp.startswith(time_tag)). \
        order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['OUSI_POSTS_PER_PAGE'], error_out=False)

    return render_template('archives.html', articles=articles, time_tag=time_tag)


@main.route('/search/', methods=['GET', 'POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('.index'))

    return redirect(url_for('.search_results', query=g.search_form.search.data.strip()))


@main.route('/search_results/<query>', methods=['GET', 'POST'])
def search_results(query):
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter(Article.body.like('%%%s%%' % query)).order_by(Article.timestamp.desc()). \
        paginate(page, per_page=current_app.config['OUSI_POSTS_PER_PAGE'], error_out=False)
    return render_template('search_result.html', articles=articles, query=query)
