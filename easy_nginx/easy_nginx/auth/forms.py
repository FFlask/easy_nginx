#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,ValidationError,SubmitField,\
    TextAreaField,SelectField,BooleanField,FileField,SelectMultipleField
from wtforms.validators import Email,EqualTo,Length,DataRequired,IPAddress
from flask_wtf.file import FileRequired,FileAllowed
from ..models import *

#登陆表单
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 64)],
                           render_kw={
                               'placeholder':'username',
                               'lay-verify':'required',
                               'class':'layui-input',
                           })
    password = PasswordField('password', validators=[DataRequired()],
                             render_kw={
                                 'placeholder': 'password',
                                 'lay-verify': 'required',
                                 'class': 'layui-input',
                             })
    submmit = SubmitField('Login',render_kw={
        'lay-submit':'',
        'lay-filter':'login',
        'style':'width:100%;'
    })

#用户增加表单
class UserAddForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 64)],
                           render_kw={
                               'placeholder':'username',
                               'lay-verify':'required',
                               'class':'layui-input',
                           })
    email = StringField('email', validators=[DataRequired(), Length(1, 64),Email()],
                           render_kw={
                               'placeholder':'email',
                               'lay-verify':'required',
                               'class':'layui-input',
                           })
    password = PasswordField('password', validators=[DataRequired()],
                             render_kw={
                                 'placeholder': 'password',
                                 'lay-verify': 'required',
                                 'class': 'layui-input',
                             })
    description = StringField('description', validators=[DataRequired(), Length(1, 64)],
                           render_kw={
                               'placeholder':'description',
                               'lay-verify':'required',
                               'class':'layui-input',
                           })
    role = SelectField(coerce=int)
    submmit = SubmitField('Add',render_kw={'class':'layui-btn',
                                          'lay-filter':'add',
                                          'lay-submit':''})

    def validate_email(self,field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError('邮箱已注册')

    def validate_username(self,field):
        if User.query.filter_by(username = field.data).first():
            raise ValidationError('用户名已注册')


    def __init__(self,*args,**kwargs):
        super(UserAddForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.role_name) for role in Role.query.order_by(Role.role_name).all()]

#用户修改表单
class UserEditForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 64)],
                           render_kw={
                               'placeholder':'username',
                               'class':'layui-input',
                               'readonly':'readonly',
                           })
    email = StringField('email', validators=[DataRequired(),],
                           render_kw={
                               'placeholder':'email',
                               'lay-verify':'required',
                               'class':'layui-input',
                           })
    password = PasswordField('password', validators=[],
                             render_kw={
                                 'placeholder': 'password',
                                 'class': 'layui-input',
                             })
    description = StringField('description', validators=[DataRequired(), Length(1, 64)],
                           render_kw={
                               'placeholder':'description',
                               'lay-verify':'required',
                               'class':'layui-input',
                           })
    role = SelectField(coerce=int)
    submmit = SubmitField('Edit',render_kw={'class':'layui-btn',
                                          'lay-filter':'edit',
                                          'lay-submit':''})

    def __init__(self,*args,**kwargs):
        super(UserEditForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.role_name) for role in Role.query.order_by(Role.role_name).all()]