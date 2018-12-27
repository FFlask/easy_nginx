#coding=utf-8
from . import db,login_manager
import datetime
from flask_login import UserMixin
from flask import request
from werkzeug.security import generate_password_hash,check_password_hash



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#角色关注表
class User2User(db.Model):
    __tablename__ = 'user2user'
    #关注的id
    follower_id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    #被关注的id
    followed_id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    #关注的时间
    create_time = db.Column(db.DateTime,default=datetime.datetime.utcnow)

#私信表
class PrivateMsg(db.Model):
    __tablename__ = 'private_msg'
    id = db.Column(db.Integer,primary_key=True,index=True)
    src_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dst_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    msg = db.Column(db.TEXT)
    create_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def __repr__(self):
        return '<PrivateMsg %r--%r--%r>'%(User.query.filter_by(id=self.src_user_id).first(),
                                          User.query.filter_by(id=self.dst_user_id).first(),
                                          self.create_time)


#用户表
class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,index=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    create_time = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime)
    description = db.Column(db.TEXT)
    head_img = db.Column(db.TEXT,default='111.jpg')
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'))
    is_star_user = db.Column(db.Boolean,default=False)
    post = db.relationship('Post',backref = 'user')
    comment = db.relationship('Comment',backref = 'user')
    zancai = db.relationship('ZanCai',backref='user')
    signin = db.relationship('SignIn',backref='user')
    chat_log = db.relationship('ChatLog',backref='user')
    #cascade删除时删除所有关联项
    #高级多对多，需要指定foreign_keys = [User2User.follower_id]，手工管理外键
    followed = db.relationship('User2User',foreign_keys = [User2User.follower_id],backref=db.backref('follower',lazy='joined'),
                               lazy='dynamic',cascade='all,delete-orphan')
    follower = db.relationship('User2User',foreign_keys = [User2User.followed_id],backref=db.backref('followed',lazy='joined'),
                               lazy='dynamic',cascade='all,delete-orphan')

    #普通一对多两组
    src_private_msg = db.relationship('PrivateMsg',foreign_keys = [PrivateMsg.src_user_id], backref='src_user')
    dst_private_msg = db.relationship('PrivateMsg', foreign_keys=[PrivateMsg.dst_user_id], backref='dst_user')
    #新增用户默认是普通用户权限
    def __init__(self,*args,**kwargs):
        super(User,self).__init__(*args,**kwargs)
        if self.role is None:
            if self.username == 'admin':
                self.role = Role.query.filter_by(role_name='Admin').first()
            else:
                self.role = Role.query.filter_by(role_name='User').first()

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def follow(self,user):
        if not self.is_following(user):
            u2u = User2User(follower_id=self.id,followed_id=user.id)
            db.session.add(u2u)
            db.session.commit()

    def unfollow(self,user):
        u2u = User2User.query.filter_by(follower_id=self.id,followed_id=user.id).first()
        if u2u:
            db.session.delete(u2u)
            db.session.commit()

    def is_following(self,user):
        return self.followed.filter_by(followed_id = user.id).first() is not None

    def is_followed_by(self,user):
        return self.follower.filter_by(follower_id = user.id).first() is not None

    def update_last_seen(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.can(Permissions.Admin)

    def is_manager(self):
        return self.can(Permissions.Manager)

    def __repr__(self):
        return '<User %r---%r>'%(self.email,self.username)

#权限类
class Permissions:
    Visit = 0x01
    Read = 0x02
    Write = 0x04
    Manager = 0x08
    Admin = 0xFF

#角色权限表
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer,primary_key=True,index=True)
    role_name = db.Column(db.String(64),unique=True,index=True)
    permissions = db.Column(db.Integer)
    user = db.relationship('User',backref='role')

    @staticmethod
    def init_role():
        roles = {
            'Visitor':Permissions.Visit,
            'User':Permissions.Visit|Permissions.Read|Permissions.Write,
            'Manager':Permissions.Visit|Permissions.Read|Permissions.Write|Permissions.Manager,
            'Admin':Permissions.Admin
        }
        for role_name,role_permissions in roles.items():
            role = Role(role_name=role_name,permissions=role_permissions)
            db.session.add(role)
            db.session.commit()

    def __repr__(self):
        return '<Role %r>'%(self.role_name)
#帖子表
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer,primary_key=True,index=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    title = db.Column(db.String(128),unique=True,index=True)
    body = db.Column(db.Text)
    create_time = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    last_modify_time = db.Column(db.DateTime)
    can_seen = db.Column(db.Boolean,default= True)
    is_best = db.Column(db.Boolean,default= False)
    is_top = db.Column(db.Boolean,default= False)
    comment = db.relationship('Comment',backref='post')
    zancai = db.relationship('ZanCai',backref='post')

    def __repr__(self):
        return '<Post %r>'%self.title
#评论表
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer,primary_key=True,index=True)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    parent_comment_id = db.Column(db.Integer,db.ForeignKey('comment.id'))
    body = db.Column(db.Text)
    create_time = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    can_seen = db.Column(db.Boolean,default=True)
    is_top_comment = db.Column(db.Boolean,default=True)
    louceng = db.Column(db.Integer)
    #自引用时需添加remote_side=[id]
    parent_comment = db.relationship('Comment',backref = 'child_comment',remote_side=[id])
    zancai = db.relationship('ZanCai',backref='comment')

    #递归返回该条评论的最顶级父评论，没有用到
    def top_comment(self):
        if self.parent_comment:
            return self.parent_comment.top_comment()
        else:
            return self

    def __repr__(self):
        return '<Comment %r>'%self.id
#点赞/踩表
class ZanCai(db.Model):
    __tablename__='zancai'
    id = db.Column(db.Integer,primary_key=True,index=True)
    #True是post，False是comment
    post_or_comment = db.Column(db.Boolean)
    # True是zan，False是cai
    zan_or_cai = db.Column(db.Boolean)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer,db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return '<ZanCai %r--%r>'%(self.id,self.zan_or_cai)

#签到表
class SignIn(db.Model):
    __tablename__ = 'signin'
    id = db.Column(db.Integer,primary_key=True,index=True)
    is_sign_in = db.Column(db.Boolean,default=True)
    create_time = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return '<SignIn %r--%r>'%(User.query.filter_by(id=self.user_id).first(),self.create_time)


#巨幕轮播图表
class Jumbotron_img(db.Model):
    __tablename__ = 'jumbotron_img'
    id = db.Column(db.Integer,primary_key=True,index=True)
    img = db.Column(db.TEXT)
    description = db.Column(db.TEXT)
    can_seen = db.Column(db.Boolean,default=False)
    def __repr__(self):
        return '<Jumbotron_img %r>'%(self.img)

#聊天记录表
class ChatLog(db.Model):
    __tablename__ = 'chat_log'
    id = db.Column(db.Integer,primary_key=True,index=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    body = db.Column(db.TEXT)
    ip = db.Column(db.String(64))
    create_time = db.Column(db.DateTime,default=datetime.datetime.utcnow)

    def __init__(self,*args,**kwargs):
        super(ChatLog,self).__init__(*args,**kwargs)
        self.ip = request.remote_addr

    def __repr__(self):
        return '<ChatLog %r--%r>'%(User.query.filter_by(id=self.user_id).first(),self.create_time)


