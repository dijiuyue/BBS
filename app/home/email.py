from app import mail
from flask import current_app,render_template
from flask_mail import Message
from threading import Thread

#异步发送
def async_send_mail(app,msg):
    #with跟上下文之间进行联系
    with app.app_context(): #自己手动加上下文
        mail.send(message=msg)

#封装函数 ,发送邮件
#参数  发给谁 主题是 给对方看的内容 其它参数
def send_mail(target,subject,templates,**kwargs):
    #获取当前app的实例
    app = current_app._get_current_object()
    #创建邮件对象
    msg = Message(subject=subject,recipients=[target],sender=app.config['MAIL_USERNAME'])
    #对方看到的内容
    msg.html = render_template(templates+'.html',**kwargs)
    msg.body = render_template(templates+'.txt',**kwargs)
    #创建线程
    thr = Thread(target=async_send_mail,args=[app,msg])
    #启动线程
    thr.start()
    return  thr
