#coding=utf-8
from flask import render_template,redirect,url_for,request,flash,abort
from . import main
from ..models import *
from .forms import InsideWebEditForm,InsideWebAddForm,OutsideWebAddForm,OutsideWebEditForm,CsrfToken
from flask_login import login_user,logout_user,login_required,current_user
import json,os
from templates_handle import config_outside_web,\
    send_modified_config,get_outside_web_conf,compare_file,\
    read_file,switch_site_state,delete_nginx_sub_conf
from config import basedir

#首页
@main.route('/')
@login_required
def index():
    return render_template('index.html')

#首页桌面
@main.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')

#生效配置
@main.route('/effect_config',methods=['GET','POST'])
@login_required
def effect_config():
    modified_outside_webs = OutsideWeb.query.filter_by(is_update=True).all()
    modified_outside_webs_dict = {}
    for modified_outside_web1 in modified_outside_webs:
        modified_outside_webs_dict.update(
            { modified_outside_web1.name :{
                'filename':modified_outside_web1.new_config_path.split('\\')[-1],
                'file':get_outside_web_conf(modified_outside_web1),
                'id':modified_outside_web1.id,
            } }
        )
    csrf_token = CsrfToken()
    if csrf_token.validate_on_submit():
        send_modified_config()
    return render_template('/main/effect_config.html',
                           modified_outside_webs_dict=modified_outside_webs_dict,
                           csrf_token=csrf_token)

#站点管理
#外部站点管理
#查
@main.route('/outside_web_list',methods=['GET','POST'])
@login_required
def outside_web_list():
    outside_webs = OutsideWeb.query.all()
    if request.method == 'POST':
        print('ok')
    return render_template('/main/outside_web_list.html',outside_webs=outside_webs)

@main.route('/outside_web_list_profile')
def outside_web_list_profile():
    cha_id = request.args.get('cha_id')
    outside_web1 = OutsideWeb.query.filter_by(id=cha_id).first()
    return render_template('/main/outside_web_list_profile.html',outside_web1=outside_web1)

#改
@main.route('/outside_web_edit',methods=['GET','POST'])
@login_required
def outside_web_edit():
    edit_id = request.args.get('edit_id')
    outside_web1 = OutsideWeb.query.filter_by(id=edit_id).first()
    outside_web_edit_form = OutsideWebEditForm()
    if outside_web_edit_form.validate_on_submit():
        inside_web_list1 = []
        for inside_web_id in outside_web_edit_form.inside_web.data:
            inside_web1 = InsideWeb.query.filter_by(id=int(inside_web_id)).first()
            inside_web_list1.append(inside_web1)
        outside_web1.description = outside_web_edit_form.description.data
        outside_web1.domain = outside_web_edit_form.domain.data
        outside_web1.port = int(outside_web_edit_form.port.data)
        outside_web1.network_protocol = int(outside_web_edit_form.network_protocol.data)
        outside_web1.application_protocol = int(outside_web_edit_form.application_protocol.data)
        outside_web1.state = int(outside_web_edit_form.state.data)
        outside_web1.inside_web = inside_web_list1
        outside_web1.update_update_time()
        config_outside_web(outside_web1)
        db.session.add(outside_web1)
        db.session.commit()
        return 'ok'
    outside_web_edit_form.name.data = outside_web1.name
    outside_web_edit_form.description.data = outside_web1.description
    outside_web_edit_form.domain.data = outside_web1.domain
    outside_web_edit_form.port.data = outside_web1.port
    outside_web_edit_form.network_protocol.data = outside_web1.network_protocol
    outside_web_edit_form.application_protocol.data = outside_web1.application_protocol
    for _inside_web in outside_web1.inside_web:
        outside_web_edit_form.inside_web.choices.append((_inside_web.id,_inside_web.name))
    outside_web_edit_form.inside_web.data = outside_web1.inside_web
    outside_web_edit_form.state.data = outside_web1.state
    return render_template('/main/outside_web_edit.html',
                           outside_web_edit_form=outside_web_edit_form,
                           outside_web1=outside_web1)

#增
@main.route('/outside_web_add',methods=['GET','POST'])
@login_required
def outside_web_add():
    outside_web_add_form = OutsideWebAddForm()
    if outside_web_add_form.validate_on_submit():
        inside_web_list1 = []
        for inside_web_id in outside_web_add_form.inside_web.data:
            inside_web1 = InsideWeb.query.filter_by(id=int(inside_web_id)).first()
            inside_web_list1.append(inside_web1)
        outside_web1 = OutsideWeb(
            name=outside_web_add_form.name.data,
            description=outside_web_add_form.description.data,
            domain=outside_web_add_form.domain.data,
            port=int(outside_web_add_form.port.data),
            network_protocol=int(outside_web_add_form.network_protocol.data),
            application_protocol=int(outside_web_add_form.application_protocol.data),
            inside_web=inside_web_list1,
            user = current_user._get_current_object(),
            state= 1
        )
        db.session.add(outside_web1)
        db.session.commit()
        outside_web1.update_update_time()
        outside_web1.create_secure_policy()
        config_outside_web(outside_web1)
    return render_template('/main/outside_web_add.html',outside_web_add_form=outside_web_add_form)

#删
@main.route('/outside_web_delete',methods=['GET','POST'])
@login_required
def outside_web_delete():
    if request.method == 'POST':
        delete_id = json.loads(request.form.get('delete_id'))
        outside_web1 = OutsideWeb.query.filter_by(id=delete_id).first()
        if outside_web1:
            outside_web1.delete_secure_policy()
            delete_nginx_sub_conf(outside_web1)
            db.session.delete(outside_web1)
            db.session.commit()
        return redirect(url_for('main.outside_web_list'))

#内部站点管理
#查
@main.route('/inside_web_list')
@login_required
def inside_web_list():
    inside_webs = InsideWeb.query.all()
    return render_template('/main/inside_web_list.html',inside_webs=inside_webs)

#改
@login_required
@main.route('/inside_web_edit',methods=['GET','POST'])
def inside_web_edit():
    inside_web_edit_form =InsideWebEditForm()
    edit_id = request.args.get('edit_id')
    inside_web1 = InsideWeb.query.filter_by(id=edit_id).first()
    if inside_web_edit_form.validate_on_submit():
        inside_web1.description = inside_web_edit_form.description.data
        inside_web1.ip = inside_web_edit_form.ip.data
        inside_web1.port = int(inside_web_edit_form.port.data)
        db.session.add(inside_web1)
        db.session.commit()
        return 'ok'
    inside_web_edit_form.name.data = inside_web1.name
    inside_web_edit_form.description.data = inside_web1.description
    inside_web_edit_form.ip.data = inside_web1.ip
    inside_web_edit_form.port.data = str(inside_web1.port)
    return render_template('/main/inside_web_edit.html',
                           inside_web_edit_form=inside_web_edit_form,
                           inside_web1=inside_web1)

#增
@main.route('/inside_web_add',methods=['GET','POST'])
@login_required
def inside_web_add():
    inside_web_add_form = InsideWebAddForm()
    if inside_web_add_form.validate_on_submit():
        inside_web1 = InsideWeb(
            name=inside_web_add_form.name.data,
            description=inside_web_add_form.description.data,
            ip=inside_web_add_form.ip.data,
            port=int(inside_web_add_form.port.data),
            user = current_user._get_current_object()
        )
        db.session.add(inside_web1)
        db.session.commit()
    return render_template('/main/secure.html',inside_web_add_form=inside_web_add_form)

#删
@main.route('/inside_web_delete',methods=['GET','POST'])
@login_required
def inside_web_delete():
    if request.method == 'POST':
        delete_id = json.loads(request.form.get('delete_id'))
        inside_web1 = InsideWeb.query.filter_by(id=delete_id).first()
        if inside_web1:
            db.session.delete(inside_web1)
            db.session.commit()
        return redirect(url_for('main.inside_web_list'))


#全局配置
#基础配置
#查
@main.route('/base_config')
@login_required
def base_config():
    base_config1 = BaseConfig.query.all()[0]
    return render_template('/main/base_config.html',base_config1=base_config1)

#查命令
@main.route('/base_config_cmd')
@login_required
def base_config_cmd():
    base_config_cmd1 = read_file(os.path.join(basedir,'easy_nginx\\static\\conf\\base_config\\base.template.conf'))
    return render_template('/main/base_config_cmd.html',base_config_cmd1=base_config_cmd1)

#改
@main.route('/base_config_edit')
@login_required
def base_config_edit():
    pass

#获取配置比对文件
@main.route('/get_compare_file')
@login_required
def get_compare_file():
    id = request.args.get('id')
    outside_web1 = OutsideWeb.query.filter_by(id=id).first()
    if outside_web1.now_config_path and outside_web1.new_config_path:
        compare_file(outside_web1.now_config_path,outside_web1.new_config_path)
        return render_template('/compare/compare.html')
    else:
        return 'new config'


#测试
@main.route('/test')
def test():
    outside_web1 = OutsideWeb.query.filter_by(id=3).first()
    compare_file(outside_web1.now_config_path,outside_web1.new_config_path)
    return render_template('/compare/compare.html')

