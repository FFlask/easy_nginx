#coding=utf-8
from flask import render_template,redirect,url_for,request,flash,abort,make_response
from . import auth
from ..models import *
from flask_login import login_user,logout_user,login_required,current_user
from forms import LoginForm,UserAddForm,UserEditForm
from decorators import is_admin,is_manager
import json

#登陆
@auth.route('/login',methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(
            username = login_form.username.data,
        ).first()
        if user and user.verify_password(login_form.password.data):
            login_user(user)
            #登陆后刷新最后登录时间
            user.update_last_seen()
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('username or password error')
    return render_template('/auth/login.html',login_form=login_form)

#登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

#用户管理
#查
@auth.route('/user_list')
@login_required
@is_admin
def user_list():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.asc()).paginate(page, per_page=5, error_out=False)
    users = pagination.items
    return render_template('/auth/user_list.html',users=users,pagination=pagination)

#增
@auth.route('/user_add',methods=['GET','POST'])
@login_required
@is_admin
def user_add():
    user_add_form = UserAddForm()
    if user_add_form.validate_on_submit():
        print(user_add_form.username.data)
        new_user = User(
            username = user_add_form.username.data,
            password = user_add_form.password.data,
            email = user_add_form.email.data,
            description = user_add_form.description.data,
            role_id = int(user_add_form.role.data)
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.user_list'))
    return render_template('/auth/user_add.html',user_add_form=user_add_form)

#改
@auth.route('/user_edit',methods=['GET','POST'])
@login_required
@is_admin
def user_edit():
    edit_id = request.args.get('edit_id')
    user1 = User.query.filter_by(id=edit_id).first()
    user_edit_form = UserEditForm()
    if user_edit_form.validate_on_submit():
        if user_edit_form.password.data:
            user1.password = user_edit_form.password.data
        user1.email = user_edit_form.email.data
        user1.description = user_edit_form.description.data
        user1.role_id = int(user_edit_form.role.data)
        db.session.add(user1)
        db.session.commit()
        return 'ok'
    user_edit_form.username.data = user1.username
    user_edit_form.email.data = user1.email
    user_edit_form.description.data = user1.description
    user_edit_form.role.data = user1.role_id
    return render_template('/auth/user_edit.html',user_edit_form=user_edit_form,user1=user1)


#删
@auth.route('/user_delete',methods=['GET','POST'])
@login_required
@is_admin
def user_delete():
    delete_id = json.loads(request.form.get('delete_id'))
    user1 = User.query.filter_by(id=delete_id).first()
    if user1:
        db.session.delete(user1)
        db.session.commit()
    return redirect(url_for('auth.user_list'))


