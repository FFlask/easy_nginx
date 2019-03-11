#coding=utf-8
from flask import render_template,redirect,url_for,request,flash,abort,make_response
from . import secure
from ..models import *
from flask_login import login_user,logout_user,login_required,current_user
from forms import SubnetActionAddForm,SecurePolicyEditForm
import json

#全局安全策略
#查
#改

#子网行为管理
#查
@secure.route('/subnet_action_list')
@login_required
def subnet_action_list():
    page = request.args.get('page', 1, type=int)
    pagination = SubnetAction.query.order_by(SubnetAction.id.asc()).paginate(page, per_page=5, error_out=False)
    subnet_actions = pagination.items
    return render_template('/secure/subnet_action_list.html',subnet_actions=subnet_actions,pagination=pagination)

#增
@secure.route('/subnet_action_add',methods=['GET','POST'])
@login_required
def subnet_action_add():
    subnet_action_add_form = SubnetActionAddForm()
    if subnet_action_add_form.validate_on_submit():
        new_subnet_action = SubnetAction(
            name= subnet_action_add_form.name.data,
            description= subnet_action_add_form.description.data,
            subnet=subnet_action_add_form.subnet.data,
            action=int(subnet_action_add_form.action.data),
            user = current_user._get_current_object(),
        )
        db.session.add(new_subnet_action)
        db.session.commit()
        return redirect(url_for('secure.subnet_action_list'))
    return render_template('/secure/subnet_action_add.html',subnet_action_add_form=subnet_action_add_form)

#删
@secure.route('/subnet_action_delete',methods=['GET','POST'])
@login_required
def subnet_action_delete():
    delete_id = json.loads(request.form.get('delete_id'))
    subnet_action1 = SubnetAction.query.filter_by(id=delete_id).first()
    if subnet_action1:
        db.session.delete(subnet_action1)
        db.session.commit()
    return redirect(url_for('secure.subnet_action_list'))


#改
@secure.route('/subnet_action_edit',methods=['GET','POST'])
@login_required
def subnet_action_edit():
    pass

#站点安全策略管理
#查
@secure.route('/secure_policy_list')
@login_required
def secure_policy_list():
    page = request.args.get('page', 1, type=int)
    pagination = SecurePolicy.query.order_by(SecurePolicy.id.asc()).paginate(page, per_page=5, error_out=False)
    secure_policys = pagination.items
    return render_template('/secure/secure_policy_list.html',secure_policys=secure_policys,pagination=pagination)

#详情
@secure.route('/secure_policy_list_profile')
@login_required
def secure_policy_list_profile():
    cha_id = request.args.get('cha_id')
    secure_policy1 = SecurePolicy.query.filter_by(id=cha_id).first()
    return render_template('/secure/secure_policy_list_profile.html',secure_policy1=secure_policy1)

#改
@secure.route('/secure_policy_edit',methods=['GET','POST'])
@login_required
def secure_policy_edit():
    secure_policy_edit_form = SecurePolicyEditForm()
    edit_id = request.args.get('edit_id')
    secure_policy1 = SecurePolicy.query.filter_by(id=edit_id).first()
    if secure_policy_edit_form.validate_on_submit():
        subnet_action_list1 = []
        for subnet_action_id in secure_policy_edit_form.subnet_action.data:
            subnet_action1 = SubnetAction.query.filter_by(id=int(subnet_action_id)).first()
            subnet_action_list1.append(subnet_action1)
        secure_policy1.id_effect = secure_policy_edit_form.is_effect.data
        secure_policy1.subnet_action = subnet_action_list1
        db.session.add(secure_policy1)
        db.session.commit()
        return 'ok'
    secure_policy_edit_form.name.data = secure_policy1.name
    secure_policy_edit_form.outside_web.data = secure_policy1.outside_web.name
    secure_policy_edit_form.user.data = secure_policy1.user.username
    secure_policy_edit_form.is_effect.data = int(secure_policy1.id_effect)
    return render_template('/secure/secure_policy_edit.html',
                           secure_policy_edit_form=secure_policy_edit_form,
                           secure_policy1=secure_policy1)


