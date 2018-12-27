#coding=utf-8
from . import bbs_admin
from .forms import LoginForm,EditManagerUserForm,SearchManagerPostForm,EditManagerPostForm,EditManagerCommentForm,EditManagerJumbotron_imgForm
from flask import render_template,redirect,url_for,flash,request
from ..models import *
from flask_login import login_user,logout_user,login_required
from decorators import is_admin,is_manager
import os

@bbs_admin.route('/admin')
@login_required
@is_manager
def admin():
    return render_template('admin.html')


@bbs_admin.route('/admin_login',methods=['GET','POST'])
def admin_login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user1 = User.query.filter_by(
            username = login_form.username.data,
            email = login_form.email.data,
            password = login_form.password.data
        ).first()
        if user1 and user1.is_manager():
            login_user(user1)
            user1.update_last_seen()
            return redirect(url_for('bbs_admin.admin'))
    return render_template('admin_login.html',login_form=login_form)

@bbs_admin.route('/manager_user')
@login_required
@is_admin
def manager_user():
    page = request.args.get('page',1,type=int)
    pagination = User.query.paginate(page,per_page=10,error_out=False)
    users = pagination.items
    return render_template('manager_user.html',users=users,pagination=pagination)

@bbs_admin.route('/edit_manager_user/<user_id>',methods=['GET','POST'])
@login_required
@is_admin
def edit_manager_user(user_id):
    edit_manager_user_form = EditManagerUserForm()
    user1 = User.query.filter_by(id = user_id).first()
    if edit_manager_user_form.validate_on_submit():
        user1.role_id = edit_manager_user_form.role.data
        user1.description = edit_manager_user_form.description.data
        user1.is_star_user = edit_manager_user_form.is_star_user.data
        db.session.add(user1)
        db.session.commit()
        return redirect(url_for('bbs_admin.manager_user'))
    edit_manager_user_form.role.data = user1.role_id
    edit_manager_user_form.description.data = user1.description
    return render_template('edit_manager_user.html',
                           user1=user1,
                           edit_manager_user_form = edit_manager_user_form)


@bbs_admin.route('/manager_post/<int:order_by_id>/<int:order_by_time>',methods=['GET','POST'])
@login_required
@is_manager
def manager_post(order_by_id,order_by_time):
    if order_by_id==1 and order_by_time==0:
        page = request.args.get('page', 1, type=int)
        pagination = Post.query.order_by(Post.id.desc()).paginate(page, per_page=10, error_out=False)
        posts = pagination.items
    elif order_by_id==0 and order_by_time==1:
        page = request.args.get('page', 1, type=int)
        pagination = Post.query.order_by(Post.create_time.desc()).paginate(page, per_page=10, error_out=False)
        posts = pagination.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Post.query.paginate(page, per_page=10, error_out=False)
        posts = pagination.items
    search_manager_post_form = SearchManagerPostForm()
    if search_manager_post_form.validate_on_submit():
        kind = search_manager_post_form.kind.data
        search_item = search_manager_post_form.search.data
        if kind=='username':
            users_ = User.query.filter(getattr(User,kind).like(('%'+'%s'%search_item+'%'))).all()
            posts_ =[]
            for user in users_:
                post1 = Post.query.filter_by(user = user).all()
                for post2 in post1:
                    posts_.append(post2)
        else:
            page = request.args.get('page', 1, type=int)
            pagination = Post.query.filter(getattr(Post,kind).like(('%'+'%s'%search_item+'%'))).paginate(page, per_page=10, error_out=False)
            posts_ = pagination.items
        return render_template('manager_post.html',
                               posts=posts_,
                               search_manager_post_form=search_manager_post_form,
                               order_by_id=order_by_id,
                               order_by_time=order_by_time,
                               pagination=pagination)
    return render_template('manager_post.html',
                           posts=posts,
                           search_manager_post_form = search_manager_post_form,
                           order_by_id=order_by_id,
                           order_by_time=order_by_time,
                           pagination=pagination)

@bbs_admin.route('/edit_manager_post/<post_id>',methods=['GET','POST'])
@login_required
@is_manager
def edit_manager_post(post_id):
    edit_manager_post_form = EditManagerPostForm()
    post1 = Post.query.filter_by(id=post_id).first()
    if edit_manager_post_form.validate_on_submit():
        post1.title = edit_manager_post_form.title.data
        post1.body = edit_manager_post_form.body.data
        post1.can_seen = edit_manager_post_form.can_seen.data
        post1.is_best = edit_manager_post_form.is_best.data
        post1.is_top = edit_manager_post_form.is_top.data
        db.session.add(post1)
        db.session.commit()
        return redirect(url_for('bbs_admin.manager_post',order_by_id=0,order_by_time=0))
    edit_manager_post_form.title.data = post1.title
    edit_manager_post_form.body.data = post1.body
    edit_manager_post_form.can_seen.data = post1.can_seen
    edit_manager_post_form.is_best.data = post1.is_best
    edit_manager_post_form.is_top.data = post1.is_top
    return render_template('edit_manager_post.html',
                           post1=post1,
                           edit_manager_post_form=edit_manager_post_form)


@bbs_admin.route('/manager_comment')
@login_required
@is_manager
def manager_comment():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.paginate(page,per_page=10,error_out=False)
    comments = pagination.items
    return render_template('manager_comment.html',
                           comments=comments,
                           pagination=pagination)

@bbs_admin.route('/edit_manager_comment/<comment_id>',methods=['GET','POST'])
@login_required
@is_manager
def edit_manager_comment(comment_id):
    edit_manager_comment_form = EditManagerCommentForm()
    comment1 = Comment.query.filter_by(id=comment_id).first()
    if edit_manager_comment_form.validate_on_submit():
        comment1.body = edit_manager_comment_form.body.data
        comment1.can_seen = edit_manager_comment_form.can_seen.data
        db.session.add(comment1)
        db.session.commit()
        return redirect(url_for('bbs_admin.manager_comment'))
    edit_manager_comment_form.body.data = comment1.body
    edit_manager_comment_form.can_seen.data = comment1.can_seen
    return render_template('edit_manager_comment.html',
                           comment1=comment1,
                           edit_manager_comment_form=edit_manager_comment_form)


@bbs_admin.route('/manager_index',methods=['GET','POST'])
@login_required
@is_manager
def manager_index():
    edit_manager_jumborn_img_form = EditManagerJumbotron_imgForm()
    star_users = User.query.filter_by(is_star_user=True).order_by(User.id.asc()).all()
    jumborn_imgs = Jumbotron_img.query.all()
    if edit_manager_jumborn_img_form.validate_on_submit():
        basepath = os.path.dirname(__file__)
        filename = edit_manager_jumborn_img_form.img.data.filename
        upload_path = os.path.join(basepath.replace('\\bbs_admin',''), 'static\\uploads', filename)
        edit_manager_jumborn_img_form.img.data.save(upload_path)
        jumbotron_img1 = Jumbotron_img(img=filename,description=edit_manager_jumborn_img_form.description.data)
        db.session.add(jumbotron_img1)
        db.session.commit()
        return redirect(url_for('bbs_admin.manager_index'))
    return render_template('manager_index.html',
                           star_users=star_users,
                           edit_manager_jumborn_img_form=edit_manager_jumborn_img_form,
                           jumborn_imgs=jumborn_imgs)



