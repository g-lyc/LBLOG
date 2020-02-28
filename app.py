# coding:utf-8

import os
import config
from flask import Flask, render_template, request, redirect, url_for, session, g
from models import User, Article, Answer
from exts import db
from decorators import login_required
from sqlalchemy import or_


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    context = {
        'articles':Article.query.order_by('-create_time').all()
    }
    return render_template('index.html',**context)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            # 加入缓存浏览其他页面时不必重复登录
            session['user_id'] = user.id
            # 如果想在31天内不需再登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'手机号码或者密码错误，请确认后登录！'


@app.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        #手机号码验证，如果注册了，就不能再注册了
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return u'该手机号码已被注册，请更换手机号码！'
        else:
            # password1要和password2相等才可以
            if password1 != password2:
                return u'两次密码不相同！'
            else:
                user = User(telephone=telephone,username=username,password=password1)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功，就让页面跳转到登陆的页面
                return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))


@app.route('/article/',methods=['GET','POST'])
@login_required
def article():
    if request.method == 'GET':
        return render_template('article.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        article = Article(title=title,content=content)
        article.author = g.user
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>/')
def detail(question_id):
    question_model = Article.query.filter(Article.id == question_id).first()
    return render_template('detail.html', question = question_model)

@app.route('/add_answer/',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    answer = Answer(content=content)
    answer.author = g.user
    question = Article.query.filter(Article.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))

@app.route('/search/')
def search():
    q = request.args.get('q')
    # title content
    articles = Article.query.filter(or_(Article.title.contains(q),Article.content.contains(q))).order_by('-create_time')
    return render_template('index.html',articles=articles)

@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user

# 钩子函数，即使为空也要返回
@app.context_processor
def my_context_processor():
    if hasattr(g,'user'):
        return {'user':g.user}
    return {}

# before_request -> 视图函数 -> context_processor


if __name__ == '__main__':
    app.run()
