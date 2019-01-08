# -*- coding: UTF-8 -*-
from flask import Flask,render_template,url_for,redirect,request,flash,get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,SelectField
from wtforms.validators import Email,EqualTo,Length,DataRequired
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_required,login_user,logout_user


app = Flask(__name__)
login_manager = LoginManager()
#设置验证强度，主要影响cookice过期时间
login_manager.session_protection = 'strong'
#设置登陆失败后的跳转
login_manager.login_view = 'index'


class Config:
    SECRET_KEY = '1a1@z2'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1/world?charset=utf8'

    #SQLALCHEMY_TRACK_MODIFICATIONS = True
    @staticmethod
    def init_app(app):
        pass

app.config.from_object(Config)
db=SQLAlchemy(app)

#数据库模型

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
login_manager.init_app(app)
#用户表
class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password unread')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User %r>'%(self.username)

#表单类
#数据库表
class DBTable(db.Model):
    __tablename__ = 'db_table'
    id = db.Column(db.Integer, primary_key=True, index=True)
    table_name = db.Column(db.String(64), unique=True)
    table_src = db.Column(db.String(64))
    def __repr__(self):
        return 'db_table <%r>'%(self.table_name)


#动态创建数据库模型
table1s = DBTable.query.all()
#把字符串变成变量
createVar = locals()
for table1 in table1s:
    #使用元类动态创建表中存储的表名
    createVar[str(table1.table_name)] = type(str(table1.table_name),(db.Model,),{
        '__tablename__':table1.table_name,
        'id':db.Column(db.Integer, primary_key=True, index=True),
        'username':db.Column(db.String(64), unique=True,index=True),
        'password':db.Column(db.String(64)),
        'email':db.Column(db.String(64), unique=True,index=True),
        })



#搜索框
class SearchForm(FlaskForm):
    search = StringField(validators=[DataRequired()],
                         render_kw={'class':'form-control',
                                    'size':'50',
                                    'placeholder':'input search content'})
    kind = SelectField(choices=[
        ('username','username'),('email','email')
    ],render_kw={'class':'form-control'})
    submmit = SubmitField('Search',render_kw={'class':'btn btn-info'})

#登陆框
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)],
                           render_kw={'class':'form-control','placeholder':'enter your username'})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={'class':'form-control','placeholder':'enter your password'})
    verify_code = StringField('CheckCode',
                              render_kw={'class': 'form-control', 'placeholder': 'zzzzzzzzz'})
    submmit = SubmitField('Login',render_kw={'class':'btn btn-info'})

#新增数据库
class DBAddForm(FlaskForm):
    table_name = StringField('table_name', validators=[DataRequired()],
                           render_kw={'class':'form-control','placeholder':'table_name'})
    table_src = StringField('table_src', validators=[DataRequired()],
                              render_kw={'class': 'form-control', 'placeholder': 'table_src'})
    submmit = SubmitField('Add',render_kw={'class':'btn btn-info'})


#业务逻辑
#初次运行时运行一下，创建admin账户
@app.route('/create_user')
def create_user():
    user1 = User.query.filter_by(username = 'admin').first()
    if not user1:
        user2 = User(username='admin',password='admin')
        db.session.add(user2)
        db.session.commit()
    return 'ok'

#测试
@app.route('/test')
def test():
    for table1 in table1s:
        for t in globals()[table1.table_name].query.all():
            print(t.username)
    return 'test'

#登陆页面
@app.route('/',methods=['GET','POST'])
def index():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user1 = User.query.filter_by(username = login_form.username.data).first()
        if user1 and user1.verify_password(login_form.password.data):
            login_user(user1)
            return redirect(request.args.get('next') or url_for('search_db'))
        else:
            flash('username or password error')
            return redirect(url_for('index'))
    return render_template('index.html',login_form=login_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#搜索页面
@app.route('/search_db',methods=['GET','POST'])
@login_required
def search_db():
    search_form = SearchForm()
    ip = request.remote_addr
    results = {}
    if search_form.validate_on_submit():
        search_item = search_form.kind.data
        for index,table1 in enumerate(DBTable.query.all()):
            try:
                #动态创建变量名
                createVar[str(table1.table_name)+str(index)] =\
                    globals()[table1.table_name].query.filter(getattr(globals()[table1.table_name],search_item)
                                                              .like('%'+'%s'%search_form.search.data+'%')).all()
                if createVar[str(table1.table_name)+str(index)] is not None:
                    results.update({table1.table_src: createVar[str(table1.table_name)+str(index)]})
            except:
                flash('Your db is not have table <%s>,Please update it!'%(str(table1.table_name)))
    return render_template('search_db.html',search_form=search_form,results=results,ip=ip)

#数据库管理/查
@app.route('/admin_db/query')
@login_required
def admin_db_query():
    return render_template('admin_db_query.html', table1s = DBTable.query.all())

#数据库管理/增
@app.route('/admin_db/add',methods=['POST','GET'])
@login_required
def admin_db_add():
    db_add_form = DBAddForm()
    if db_add_form.validate_on_submit():
        new_table = DBTable(
            table_name=db_add_form.table_name.data,
            table_src=db_add_form.table_src.data,
        )
        db.session.add(new_table)
        db.session.commit()
        return redirect(url_for('admin_db_query'))
    return render_template('admin_db_add.html',db_add_form=db_add_form)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
