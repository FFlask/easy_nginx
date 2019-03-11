#coding=utf-8
import jinja2
from .. import db
from ..models import *
import datetime,os
from config import basedir,nginx_path
import difflib,subprocess,commands,requests


#生成反代站点配置文件，每次新增或者修改反代站点时添加
#并更新数据库反代站点的new_config_path为最新生成的配置文件路径
#反代站点的是否更新状态为是
def config_outside_web(outside_web):
    with open(os.path.join(basedir,'easy_nginx/static/conf_templates/proxy.template'), 'r') as rf1:
        template = jinja2.Template(rf1.read())
        b = template.render(outside_web_domain=outside_web.domain,
                            inside_webs = outside_web.inside_web,
                            outside_web_port = outside_web.port,
                            )
        if not os.path.exists(os.path.join(basedir,'easy_nginx/static/conf/%s'%(outside_web.name))):
            os.mkdir(os.path.join(basedir,'easy_nginx/static/conf/%s'%(outside_web.name)))
        new_config_path = os.path.join(basedir,'easy_nginx/static/conf/%s/%s_%s.conf'%(outside_web.name,outside_web.domain,datetime.datetime.now().strftime('%Y-%b-%d-%H-%M-%S')))
        with open(new_config_path, 'w+') as wf:
            wf.write(b)
        outside_web.new_config_path = new_config_path
        outside_web.is_update = True
        db.session.add(outside_web)
        db.session.commit()

#查询数据库中所有基础及反代配置文件
#把所有最新配置的文件发送到服务器
#更新数据库反代站点是否更新为否,now_config_path为new_config_path
def send_modified_config():
    modified_outside_webs = OutsideWeb.query.filter_by(is_update=True).all()
    if modified_outside_webs:
        for modified_outside_web1 in modified_outside_webs:
            send_config(modified_outside_web1)
            modified_outside_web1.is_update = False
            modified_outside_web1.now_config_path = modified_outside_web1.new_config_path
            db.session.add(modified_outside_web1)
            db.session.commit()

#获取反代配置文件内容
def get_outside_web_conf(outside_web):
    conf_file = ''
    with open(outside_web.new_config_path,'r') as rf:
        for line in rf.readlines():
            if line[0] == " ":
                line = "&nbsp;&nbsp;&nbsp;&nbsp;" + line
            line += '<br>'
            conf_file+= line
    return conf_file

#读文件
def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except IOError:
        print("ERROR: 没有找到文件:%s或读取文件失败！" % filename)


#对比文本差异
def compare_file(file1, file2):
    file1_content = read_file(file1)
    file2_content = read_file(file2)
    d = difflib.HtmlDiff()
    result = d.make_file(file1_content, file2_content)
    out_file = os.path.join(basedir,'easy_nginx/templates/compare/compare.html')
    with open(out_file, 'w') as f:
        f.writelines(result)


#发送配置
def send_config(outside_web):
    with open(outside_web.new_config_path,'r') as rf:
        with open(os.path.join(nginx_path,'conf.d/%s.conf'%outside_web.domain),'w') as wf:
            wf.write(rf.read())
    switch_site_state(outside_web)
    reload_nignx()
    print('Sending config path is conf.d/%s.conf'%outside_web.domain)

#生效/失效站点
#失效：把站点的配置后缀从.conf变成.conf.disable
#生效：把站点的配置后缀从.conf.disable变成.conf
def switch_site_state(outside_web):
    site_state = outside_web.state
    if site_state == 2:
        subprocess.call("mv %s %s"%((outside_web.domain+'.conf'),(outside_web.domain+'.conf_disable')), shell=True, cwd=os.path.join(nginx_path,'conf.d'), )
    elif site_state == 1:
        subprocess.call("mv %s %s"%((outside_web.domain+'.conf_disable'),(outside_web.domain+'.conf')), shell=True, cwd=os.path.join(nginx_path,'conf.d'), )

#服务器状态显示
def show_server_state():
    pass

#nginx重载
def reload_nignx():
    subprocess.call("nginx -s reload",shell=True,)

#linux命令运行
def run_shell(cmd):
    (status,output) = commands.getstatusoutput(cmd)
    context = {
        "status":status,
        "output":output
    }
    return context

#nginx语法检查是否通过
def nginx_state():
    nginx_state1 = run_shell('nginx -t')['output']
    if 'successful' and 'ok' in nginx_state1:
        return True
    else:
        return False

#nginx删除子配置文件
def delete_nginx_sub_conf(outside_web):
    site_state = outside_web.state
    if site_state == 1:
        subprocess.call("rm %s" % (outside_web.domain + '.conf'),shell=True, cwd=os.path.join(nginx_path, 'conf.d'), )
    elif site_state == 2:
        subprocess.call("rm %s" % (outside_web.domain + '.conf_disable'), shell=True, cwd=os.path.join(nginx_path, 'conf.d'), )


