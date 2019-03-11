#coding=utf-8
from easy_nginx import db,create_app
from easy_nginx.models import *
app = create_app()

with app.app_context():
    db.drop_all()
    #根据模型创建数据表
    db.create_all()
    #初始化角色表
    Role.init_role()
    #创建admin用户
    user_admin = User(
        username = 'admin',
        password = 'admin',
        email = 'admin@qq.com',
        description = 'GOD',
        role_id = 1
    )
    db.session.add(user_admin)
    db.session.commit()

