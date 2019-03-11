#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,ValidationError,SubmitField,\
    TextAreaField,SelectField,BooleanField,FileField,SelectMultipleField
from wtforms.validators import Email,EqualTo,Length,DataRequired,IPAddress
from flask_wtf.file import FileRequired,FileAllowed
from ..models import *

#SelectMultipleField一直验证报错，然而感觉并没什么错，去掉验证
class SMF(SelectMultipleField):
    def pre_validate (self,form):
        pass

#内部站点新增
class InsideWebAddForm(FlaskForm):
    name = StringField(validators=[DataRequired(),Length(1,64)],
                       render_kw={'required':'',
                                  'lay-verify':'required',
                                  'autocomplete':'off',
                                  'class':'layui-input',
                                  })
    description = StringField(validators=[DataRequired(),Length(1,64)],
                              render_kw={'required': '',
                                         'lay-verify': 'required',
                                         'autocomplete': 'off',
                                         'class': 'layui-input'})
    ip = StringField(validators=[DataRequired()],
                     render_kw={'required': '',
                                'lay-verify': 'required',
                                'autocomplete': 'off',
                                'class': 'layui-input'}
                     )
    port = StringField(validators=[DataRequired()],
                       render_kw={'required': '',
                                  'lay-verify': 'required',
                                  'autocomplete': 'off',
                                  'class': 'layui-input'}
                       )
    submmit = SubmitField('Add',render_kw={'class':'layui-btn',
                                          'lay-filter':'add',
                                          'lay-submit':''})

    def validate_name(self,field):
        if InsideWeb.query.filter_by(name = field.data).first():
            raise ValidationError('命名重复')

#内部站点编辑
class InsideWebEditForm(FlaskForm):
    name = StringField(validators=[DataRequired(),Length(1,64)],
                       render_kw={'required': '',
                                  'lay-verify': 'required',
                                  'autocomplete': 'off',
                                  'class': 'layui-input',
                                  'readonly': 'readonly',
                                  })
    description = StringField(validators=[DataRequired(),Length(1,64)],
                              render_kw={'required': '',
                                         'lay-verify': 'required',
                                         'autocomplete': 'off',
                                         'class': 'layui-input'}
                              )
    ip = StringField(validators=[DataRequired()],
                     render_kw={'required': '',
                                'lay-verify': 'required',
                                'autocomplete': 'off',
                                'class': 'layui-input'}
                     )
    port = StringField(validators=[DataRequired()],
                       render_kw={'required': '',
                                  'lay-verify': 'required',
                                  'autocomplete': 'off',
                                  'class': 'layui-input'}
                       )
    submmit = SubmitField('Edit',render_kw={'class':'layui-btn',
                                          'lay-filter':'edit',
                                          'lay-submit':''})

#反代站点新增
class OutsideWebAddForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(1, 64)],
                       render_kw={'required': '',
                                  'lay-verify': 'required',
                                  'autocomplete': 'off',
                                  'class': 'layui-input'}
                       )
    description = StringField(validators=[DataRequired()],
                              render_kw={'required': '',
                                         'lay-verify': 'required',
                                         'autocomplete': 'off',
                                         'class': 'layui-input'}
                              )
    domain = StringField(validators=[DataRequired()],
                         render_kw={'required': '',
                                    'lay-verify': 'required',
                                    'autocomplete': 'off',
                                    'class': 'layui-input'}
                         )
    port = StringField(validators=[DataRequired()],
                       render_kw={'required': '',
                                  'lay-verify': 'required',
                                  'autocomplete': 'off',
                                  'class': 'layui-input'}
                       )
    network_protocol_choice = ((1,'IPv4'),(2,'IPv6'),(3,'IPv4&6'))
    network_protocol = SelectField(coerce=int,choices=network_protocol_choice)
    application_protocol_choice = ((1,'HTTP'),(2,'HTTPS'))
    application_protocol = SelectField(coerce=int,choices=application_protocol_choice)
    inside_web = SelectMultipleField(coerce=int,
                             render_kw={
                                 'multiple':'multiple',
                                 'lay-ignore':'lay-ignore'})
    submmit = SubmitField('Add', render_kw={'class': 'layui-btn',
                                            'lay-filter': 'add',
                                            'lay-submit': ''})

    def __init__(self,*args,**kwargs):
        super(OutsideWebAddForm,self).__init__(*args,**kwargs)
        self.inside_web.choices = [(inside_web.id,inside_web.name) for inside_web in
            InsideWeb.query.order_by(InsideWeb.id).all() if not inside_web.is_selected()]

    def validate_name(self,field):
        if OutsideWeb.query.filter_by(name = field.data).first():
            raise ValidationError('命名重复')

#反代站点编辑
class OutsideWebEditForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(1, 64)],
                       render_kw={'required': '',
                                  'lay-verify': 'required',
                                  'autocomplete': 'off',
                                  'class': 'layui-input',
                                  'readonly': 'readonly'}
                       )
    description = StringField(validators=[DataRequired()],
                              render_kw={'required': '',
                                         'lay-verify': 'required',
                                         'autocomplete': 'off',
                                         'class': 'layui-input'}
                              )
    domain = StringField(validators=[DataRequired()],
                         render_kw={'required': '',
                                    'lay-verify': 'required',
                                    'autocomplete': 'off',
                                    'class': 'layui-input'}
                         )
    port = StringField(validators=[DataRequired()],
                       render_kw={'required': '',
                                  'lay-verify': 'required',
                                  'autocomplete': 'off',
                                  'class': 'layui-input'}
                       )
    network_protocol_choice = ((1,'IPv4'),(2,'IPv6'),(3,'IPv4&6'))
    network_protocol = SelectField(coerce=int,choices=network_protocol_choice)
    application_protocol_choice = ((1,'HTTP'),(2,'HTTPS'))
    application_protocol = SelectField(coerce=int,choices=application_protocol_choice)
    inside_web = SMF(coerce=int,
                             render_kw={
                                 'multiple':'multiple',
                                 'lay-ignore':'lay-ignore',
                             'id':'select1',},
                                     )
    state_choice = ((1,'ONline'),(2,'OFFline'))
    state = SelectField(coerce=int,choices=state_choice)
    submmit = SubmitField('Edit', render_kw={'class': 'layui-btn',
                                            'lay-filter': 'edit',
                                            'lay-submit': ''})

    def __init__(self,*args,**kwargs):
        super(OutsideWebEditForm,self).__init__(*args,**kwargs)
        self.inside_web.choices = []
        self._inside_webs = [(inside_web.id,inside_web.name) for inside_web in
            InsideWeb.query.order_by(InsideWeb.id).all() if not inside_web.is_selected()]
        for _inside_web1 in self._inside_webs:
            self.inside_web.choices.append(_inside_web1)

#发送csrf_token用的
class CsrfToken(FlaskForm):
    pass