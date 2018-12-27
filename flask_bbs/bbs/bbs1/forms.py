#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,ValidationError,SubmitField,TextAreaField,SelectField,BooleanField,FileField
from wtforms.validators import Email,EqualTo,Length,DataRequired
from flask_wtf.file import FileRequired,FileAllowed
from ..models import *

class RegisterForm(FlaskForm):
    email = StringField('邮箱：',validators=[DataRequired(),Length(1,64),Email()],render_kw={'class':'form-control'})
    username = StringField('用户名：',validators=[DataRequired(),Length(1,64)],render_kw={'class':'form-control'})
    password = PasswordField('密码：',validators=[DataRequired(),EqualTo('password2','密码输入不一致')],render_kw={'class':'form-control'})
    password2 = PasswordField('重复密码：',validators=[DataRequired()],render_kw={'class':'form-control'})
    submmit = SubmitField('注册',render_kw={'class':'btn btn-info'})

    def validate_email(self,field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError('邮箱已注册')

    def validate_username(self,field):
        if User.query.filter_by(username = field.data).first():
            raise ValidationError('用户名已注册')


class LoginForm(FlaskForm):
    email = StringField('邮箱：', validators=[DataRequired(), Length(1, 64), Email()],render_kw={'class':'form-control'})
    username = StringField('用户名：', validators=[DataRequired(), Length(1, 64)],render_kw={'class':'form-control'})
    password = PasswordField('密码：', validators=[DataRequired()],render_kw={'class':'form-control'})
    submmit = SubmitField('登录',render_kw={'class':'btn btn-info'})

class EditProfileForm(FlaskForm):
    description = TextAreaField('个人简介：',render_kw={'class':'form-control'})
    head_img = FileField('上传头像:',validators=[FileRequired(),
                                             FileAllowed(['jpg', 'png'], '只接收.jpg和.png格式的简历')],
                         render_kw={'class':'form-control'})
    submmit = SubmitField('提交',render_kw={'class':'btn btn-info'})

class EditPostForm(FlaskForm):
    title = StringField('标题：',validators=[DataRequired()],render_kw={'class':'form-control'})
    body = TextAreaField('帖子内容：',validators=[DataRequired()],render_kw={'class':'form-control'})
    submmit = SubmitField('提交',render_kw={'class':'btn btn-info'})

class EditComment(FlaskForm):
    body = TextAreaField(validators=[DataRequired()],
                         render_kw={'class':'form-control input-lg','row':'3','placeholder':'评论内容'})
    submmit = SubmitField('提交评论',render_kw={'class':'btn btn-info'})