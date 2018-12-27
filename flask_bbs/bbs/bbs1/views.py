#coding=utf-8
from flask import render_template,redirect,url_for,request,flash,abort,make_response
from . import bbs1
from forms import RegisterForm,LoginForm,EditProfileForm,EditPostForm,EditComment
from ..models import *
from flask_login import login_user,logout_user,login_required,current_user
import os,json,datetime,hashlib
from  geventwebsocket.websocket import WebSocket,WebSocketError

@bbs1.route('/')
def index():
    star_users = User.query.filter_by(is_star_user=True).order_by(User.id.asc()).all()
    jumbotron_imgs = Jumbotron_img.query.filter_by(can_seen=True).order_by(Jumbotron_img.id).all()
    return render_template('index.html',star_users=star_users,jumbotron_imgs=jumbotron_imgs)

@bbs1.route('/register',methods=['GET','POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User(
            email = register_form.email.data,
            username = register_form.username.data,
            password = register_form.password.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('bbs1.login'))
    return render_template('register.html',register_form=register_form)


@bbs1.route('/login',methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(
            username = login_form.username.data,
            email = login_form.email.data
        ).first()
        if user and user.verify_password(login_form.password.data):
            login_user(user)
            user.update_last_seen()
            return redirect(request.args.get('next') or url_for('bbs1.index'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html',login_form=login_form)

@bbs1.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('bbs1.index'))

@bbs1.route('/user/<username>')
def user(username):
    user1 = User.query.filter_by(username=username).first()
    if user1==None:
        abort(404)
    return render_template('user.html',user1=user1)

@bbs1.route('/user/<username>/userprofile')
def userprofile(username):
    user1 = User.query.filter_by(username=username).first()
    if user1==None:
        abort(404)
    return render_template('userprofile.html',user1=user1)

@bbs1.route('/user/<username>/userprofile/user_edit_profile',methods=['GET','POST'])
@login_required
def user_edit_profile(username):
    edit_profile_profile = EditProfileForm()
    user1 = User.query.filter_by(username=username).first()
    if user1==None:
        abort(404)
    if edit_profile_profile.validate_on_submit() and current_user.username == user1.username:
        user1.description = edit_profile_profile.description.data
        # filename = edit_profile_profile.head_img.data.filename
        salt = 'salt11'
        m = hashlib.md5()
        m.update(str(datetime.datetime.now())+salt)
        filename = m.hexdigest()+'.jpg'
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath.replace('\\bbs1',''), 'static\\uploads', filename)
        edit_profile_profile.head_img.data.save(upload_path)
        user1.head_img = filename
        db.session.add(user1)
        db.session.commit()
        return redirect(url_for('bbs1.userprofile',username=username))
    edit_profile_profile.head_img.data = user1.head_img
    edit_profile_profile.description.data = user1.description
    return render_template('user_edit_profile.html',user1=user1,edit_profile_profile=edit_profile_profile)

@bbs1.route('/edit_post',methods=['GET','POST'])
@login_required
def edit_post():
    edit_post_form = EditPostForm()
    if edit_post_form.validate_on_submit():
        post = Post(
            user = current_user,
            title=edit_post_form.title.data,
            body=edit_post_form.body.data
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('bbs1.post'))
    return render_template('edit_post.html',edit_post_form=edit_post_form)

@bbs1.route('/post')
def post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.id.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template('post.html',posts = posts,pagination=pagination)

@bbs1.route('/zancai',methods=['GET','POST'])
@login_required
def zancai():
    if request.method == 'POST':
        post_or_comment = request.form.get('post_or_comment')
        id = request.form.get('post_id')
        zan_or_cai = request.form.get('zan_or_cai')
        zancai2 = ZanCai.query.filter_by(
            user=current_user._get_current_object(),
            post_id=id,
            post_or_comment=bool(post_or_comment),
            zan_or_cai=bool(zan_or_cai)
        ).first()
        #已经点赞则返回已点赞
        if zancai2:
            message = {'state': 'fail'}
            return make_response(json.dumps(message))
        #没有点赞的则点赞
        else:
            zancai1 = ZanCai(
                user = current_user._get_current_object(),
                post_id = id,
                post_or_comment= bool(post_or_comment),
                zan_or_cai=bool(zan_or_cai)
                )
            db.session.add(zancai1)
            db.session.commit()
            message = {'state': 'success'}
            return make_response(json.dumps(message))


@bbs1.route('/user/<username>/user_post')
def user_post(username):
    user1 = User.query.filter_by(username=username).first()
    #post1 = Post.query.filter_by(user=user1).all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(user=user1).order_by(Post.id.asc()).paginate(page, per_page=5, error_out=False)
    post1= pagination.items
    return render_template('user_post.html',post1=post1,user1=user1,pagination=pagination)


@bbs1.route('/comment/<post_id>',methods=['GET','POST'])
def comment(post_id):
    edit_comment = EditComment()
    post1 = Post.query.filter_by(id=post_id).first()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(post=post1).order_by(Comment.id.asc()).paginate(page, per_page=5, error_out=False)
    comments= pagination.items
    if edit_comment.validate_on_submit() and current_user._get_current_object():
        #查找最新一条评论，新评论的楼层为最新一条评论的楼层+1
        last_comment = Comment.query.filter_by(post_id=post_id).order_by(Comment.louceng.desc()).first()
        if last_comment is None:
            last_comment_louceng = 0
        else:
            last_comment_louceng = last_comment.louceng
        comment1 = Comment(
            body=edit_comment.body.data,
            post = post1,
            user = current_user._get_current_object(),
            louceng=last_comment_louceng + 1
        )
        db.session.add(comment1)
        db.session.commit()
        return redirect(url_for('bbs1.comment',post_id=post1.id))
    return render_template('comment.html',post1=post1,comments=comments,
                           edit_comment=edit_comment,
                           pagination=pagination)

#发表子评论，接收前端发来的ajax数据
@bbs1.route('/comment/<post_id>/edit_child_comment',methods=['GET','POST'])
@login_required
def edit_child_comment(post_id):
    if request.method == 'POST':
        comment_id = request.form.get('comment_id')
        edit_child_comment = request.form.get('edit_child_comment')
        last_comment = Comment.query.filter_by(post_id=post_id).order_by(Comment.louceng.desc()).first()
        last_comment_louceng=last_comment.louceng
        if last_comment is None:
            last_comment_louceng=0
        else:
            last_comment_louceng = last_comment.louceng
        #current_user._get_current_object()代表真正的User对象
        child_comment1 = Comment(
            user = current_user._get_current_object(),
            is_top_comment=False,
            post_id = post_id,
            parent_comment_id=comment_id,
            body=edit_child_comment,
            louceng=last_comment_louceng+1
        )
        db.session.add(child_comment1)
        db.session.commit()
        message = { 'state':'success' }
        return make_response(json.dumps(message))

@bbs1.route('/user/<username>/user_comment')
def user_comment(username):
    user1 = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(user=user1).order_by(Comment.id.asc()).paginate(page, per_page=5, error_out=False)
    user_comments= pagination.items
    return render_template('user_comment.html',user_comments =user_comments,user1=user1,pagination=pagination)

@bbs1.route('/user/<username>/follow')
@login_required
def follow(username):
    user1 = current_user._get_current_object()
    user2 = User.query.filter_by(username = username).first()
    if not user1.is_following(user2):
        print user1.is_following(user2)
        user1.follow(user2)
    return redirect(request.args.get('next') or url_for('bbs1.userprofile',username=username))

@bbs1.route('/user/<username>/unfollow')
@login_required
def unfollow(username):
    user1 = current_user._get_current_object()
    user2 = User.query.filter_by(username = username).first()
    if  user1.is_following(user2):
        user1.unfollow(user2)
    return redirect(request.args.get('next') or url_for('bbs1.userprofile',username=username))

@bbs1.route('/user/<username>/user_followers')
@login_required
def user_followers(username):
    user1 = User.query.filter_by(username=username).first()
    followers = user1.followed.all()
    return render_template('user_followers.html',user1=user1,followers = followers)


def create_comment_tree():
    ret = []
    comment_list_dict = {}
    comments = Comment.query.all()
    for comment in comments:
        if comment.is_top_comment:
            comment_list_dict.update({comment.id:{}})

@bbs1.route('/test1')
def test1():
    comments = Comment.query.all()
    for comment in comments:
        if comment.top_comment():
            print(comment.top_comment())
    return render_template('test1.html')



@bbs1.route('/signin/<username>',methods=['GET','POST'])
@login_required
def signin(username):
    user1 = User.query.filter_by(username=username).first()
    signin1 = SignIn.query.filter_by(user=user1).order_by(SignIn.create_time.desc()).first()
    day1 = datetime.timedelta(days=1)

    #打开页面时，使用ajax发送post请求来确定签到的状态
    #大于一天可以签到且之前签过到才可以继续签到，没签过到的之前跳过
    if request.method == 'POST' and signin1 and signin1.create_time - datetime.datetime.utcnow()>day1:
        is_sign_in = True
        return make_response(json.dumps({'status': is_sign_in}))
    elif request.method == 'POST' and signin1:
        is_sign_in = False
        sign_sum = SignIn.query.filter_by(user=user1).count()
        return make_response(json.dumps({'status': is_sign_in,'sign_sum':str(sign_sum)}))

    #get请求用来签到
    if signin1 is None:
        new_sign_in = SignIn(user=user1)
        db.session.add(new_sign_in)
        db.session.commit()
    if signin1 and signin1.create_time - datetime.datetime.utcnow()>day1:
        new_sign_in = SignIn(user=user1)
        db.session.add(new_sign_in)
        db.session.commit()
    return redirect(request.args.get('next') or url_for('bbs1.index'))



user_socket_dict={}

@bbs1.route('/ws/<username>')
def ws(username):
    user_socket=request.environ.get("wsgi.websocket")
    if not user_socket:
        return "请以WEBSOCKET方式连接"

    user_socket_dict[username]=user_socket
    print(user_socket_dict.get(username))

    while True:
        try:
            user_msg = user_socket.receive()
            if user_msg:
                chat_log1 = ChatLog(body=user_msg,user=current_user._get_current_object())
                db.session.add(chat_log1)
                db.session.commit()
            #循环用户表，将接收到的信息广播给所有用户
            for user_name,u_socket in user_socket_dict.items():

                who_send_msg={
                    "send_user":username,
                    "send_msg":user_msg
                }
                #接收到自己发给自己的数据则跳过此次循环
                if user_socket == u_socket:
                    continue
                u_socket.send(json.dumps(who_send_msg))

        except WebSocketError as e:
            user_socket_dict.pop(username)
            print('%s is leave'%(user_socket_dict))

