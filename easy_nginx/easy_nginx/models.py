#coding=utf-8
from . import db,login_manager
import datetime,requests
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import current_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#用户表
class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,index=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    create_time = db.Column(db.DateTime,default=datetime.datetime.now)
    last_seen = db.Column(db.DateTime)
    description = db.Column(db.String(128))
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'))
    inside_web = db.relationship('InsideWeb',backref = 'user')
    outside_web = db.relationship('OutsideWeb', backref='user')
    subnet_action = db.relationship('SubnetAction',backref='user')
    secure_policy = db.relationship('SecurePolicy',backref='user')
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
        raise AttributeError('error unread')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def update_last_seen(self):
        self.last_seen = datetime.datetime.now()
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

#内部站点表
class InsideWeb(db.Model):
    __tablename__ = 'inside_web'
    id = db.Column(db.Integer,primary_key=True,index=True)
    name = db.Column(db.String(64),unique=True,index=True)
    description = db.Column(db.String(128))
    ip = db.Column(db.String(32))
    port = db.Column(db.Integer)
    create_time = db.Column(db.DateTime,default=datetime.datetime.now)
    update_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    outside_web_id = db.Column(db.Integer, db.ForeignKey('outside_web.id'))

    def update_update_time(self):
        self.update_time = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def is_selected(self):
        if self.outside_web_id:
            return True
        else:
            return False

    # 内部站点检查
    def state_check(self):
        try:
            res = requests.head('http://%s:%s' % (self.ip, self.port),timeout=0.1)
            return True
        except:
            return False


    def __repr__(self):
        return '<InsideWeb %r>' % (self.name)

#反代站点表
class OutsideWeb(db.Model):
    __tablename__ = 'outside_web'
    id = db.Column(db.Integer,primary_key=True,index=True)
    name = db.Column(db.String(64),unique=True,index=True)
    description = db.Column(db.String(128))
    domain = db.Column(db.String(64),unique=True)
    port = db.Column(db.Integer)
    network_protocol_choice = { 1:'IPv6',2:'IPv4',3:'IPv4&6'}
    network_protocol = db.Column(db.Integer)
    application_protocol_choice = {1:'HTTP',2:'HTTPS'}
    application_protocol = db.Column(db.Integer)
    state_choice = {1:'ONline',2:'OFFline'}
    state = db.Column(db.Integer)
    now_config_path = db.Column(db.String(128))
    new_config_path = db.Column(db.String(128))
    is_update = db.Column(db.Boolean,default=False)
    create_time = db.Column(db.DateTime,default=datetime.datetime.now)
    update_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    inside_web = db.relationship('InsideWeb', backref='outside_web')
    secure_policy = db.relationship('SecurePolicy',backref='outside_web',uselist=False)

    def update_update_time(self):
        self.update_time = datetime.datetime.now()
        self.is_update = True
        db.session.add(self)
        db.session.commit()

    #创建反代站点时，创建空的安全策略
    def create_secure_policy(self):
        new_secure_policy  = SecurePolicy(
            name= '%s_secure_policy'%self.name,
            description='%s_secure_policy'%self.name,
            outside_web_id=self.id,
            user = current_user._get_current_object(),
            id_effect=False,
        )
        db.session.add(new_secure_policy)
        db.session.commit()

    #删除反代站点时，删除相关的安全策略
    def delete_secure_policy(self):
        secure_policy1 = SecurePolicy.query.filter_by(outside_web_id=self.id).first()
        if secure_policy1:
            db.session.delete(secure_policy1)
            db.session.commit()

    def __repr__(self):
        return '<OutsideWeb %r>' % (self.name)


#基础配置表
class BaseConfig(db.Model):
    __tablename__ = 'base_config'
    id = db.Column(db.Integer,primary_key=True,index=True)
    worker_processes = db.Column(db.Integer)
    worker_connections = db.Column(db.Integer)
    keepalive_timeout = db.Column(db.Integer)
    client_max_body_size = db.Column(db.Integer)
    update_time = db.Column(db.DateTime)

    def update_update_time(self):
        self.update_time = datetime.datetime.now()
        self.is_update = True
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<BaseConfig %r>' % (self.id)


#安全配置
#安全基础配置
class BaseSecureConfig(db.Model):
    __tablename__ = 'base_secure_config'
    id = db.Column(db.Integer, primary_key=True, index=True)
    def __repr__(self):
        return '<BaseSecureConfig %r>' % (self.id)

#子网-行为表
class SubnetAction(db.Model):
    __tablename__ = 'subnet_action'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64),unique=True,index=True)
    description = db.Column(db.String(128))
    subnet = db.Column(db.String(128),index=True)
    action_choice = {1: 'allow', 2: 'deny'}
    action = db.Column(db.Integer)
    secure_policy_id = db.Column(db.Integer, db.ForeignKey('secure_policy.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __table_args__ = (db.UniqueConstraint('subnet', 'action', name='subnet_action'),db.Index('subnet', 'action'),)
    def __repr__(self):
        return '<SubnetAction %r>' % (self.name)

#安全策略表
class SecurePolicy(db.Model):
    __tablename__ = 'secure_policy'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64),unique=True,index=True)
    description = db.Column(db.String(128))
    outside_web_id = db.Column(db.Integer, db.ForeignKey('outside_web.id'))
    subnet_action = db.relationship('SubnetAction',backref='secure_policy')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_effect = db.Column(db.Boolean)
    def __repr__(self):
        return '<SecurePolicy %r>' % (self.name)