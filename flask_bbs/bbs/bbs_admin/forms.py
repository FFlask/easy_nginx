#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,ValidationError,SubmitField,TextAreaField,SelectField,BooleanField,FileField
from wtforms.validators import Email,EqualTo,Length,DataRequired
from flask_wtf.file import FileRequired
from ..models import *

class LoginForm(FlaskForm):
    email = StringField('邮箱：', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名：', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码：', validators=[DataRequired()])
    submmit = SubmitField('登录')

class EditManagerUserForm(FlaskForm):
    role = SelectField(coerce=int)
    description = StringField()
    is_star_user = BooleanField()
    submmit = SubmitField('提交')

    def __init__(self,*args,**kwargs):
        super(EditManagerUserForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.role_name) for role in Role.query.order_by(Role.role_name).all()]


class SearchManagerPostForm(FlaskForm):
    search = StringField(validators=[DataRequired()])
    kind = SelectField(choices=[
        ('id','ID'),('username','作者'),('title','标题'),('body','内容'),('create_time','创建时间'),
    ])
    submmit = SubmitField('查询')

class EditManagerPostForm(FlaskForm):
    title = StringField()
    body = StringField()
    can_seen = BooleanField()
    is_best = BooleanField()
    is_top = BooleanField()
    submmit = SubmitField('提交')

class EditManagerCommentForm(FlaskForm):
    body = StringField()
    can_seen = BooleanField()
    submmit = SubmitField('提交')

class EditManagerJumbotron_imgForm(FlaskForm):
    img = FileField(validators=[FileRequired()])
    can_seen = BooleanField()
    description = StringField('描述：')
    submmit = SubmitField('新增')