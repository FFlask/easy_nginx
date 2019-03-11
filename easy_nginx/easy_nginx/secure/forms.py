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

#子网行为增加表单
class SubnetActionAddForm(FlaskForm):
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
    subnet = StringField(validators=[DataRequired()],
                     render_kw={'required': '',
                                'lay-verify': 'required',
                                'autocomplete': 'off',
                                'class': 'layui-input'}
                     )

    action_choice = ((1,'allow'),(2,'deny'))
    action = SelectField(coerce=int,choices=action_choice)

    submmit = SubmitField('Add',render_kw={'class':'layui-btn',
                                          'lay-filter':'add',
                                          'lay-submit':''})

    def validate_name(self,field):
        if InsideWeb.query.filter_by(name = field.data).first():
            raise ValidationError('命名重复')


#反代安全策略编辑表单
class SecurePolicyEditForm(FlaskForm):
    name = StringField(validators=[DataRequired(),Length(1,64)],
                       render_kw={'required':'',
                                  'readonly':'readonly',
                                  'autocomplete':'off',
                                  'class':'layui-input',
                                  })
    outside_web = StringField(validators=[DataRequired()],
                     render_kw={'required': '',
                                'readonly':'readonly',
                                'autocomplete': 'off',
                                'class': 'layui-input'}
                     )

    is_effect_choice = ((1,'Effect'),(0,'UnEffect'))
    is_effect = SelectField(coerce=int,choices=is_effect_choice)
    subnet_action = SelectMultipleField(coerce=int,
                             render_kw={
                                 'multiple':'multiple',
                                 'lay-ignore':'lay-ignore',
                                 'id': 'select1',})

    user = StringField(validators=[DataRequired()],
                     render_kw={'required': '',
                                'readonly':'readonly',
                                'autocomplete': 'off',
                                'class': 'layui-input'}
                     )

    submmit = SubmitField('Edit',render_kw={'class':'layui-btn',
                                          'lay-filter':'edit',
                                          'lay-submit':''})

    def __init__(self,*args,**kwargs):
        super(SecurePolicyEditForm,self).__init__(*args,**kwargs)
        self.subnet_action.choices = [(subnet_action.id,('%s--%s'%(subnet_action.subnet,subnet_action.action_choice.get(subnet_action.action))))
                                      for subnet_action in SubnetAction.query.order_by(SubnetAction.id).all()]