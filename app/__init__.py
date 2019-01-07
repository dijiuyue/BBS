#coding:utf8
#用app下的__init__.py注册蓝图
from flask import Flask,render_template
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from  flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash
from datetime import datetime
import time
import os
#from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail
from flask_moment import  Moment
#app.debug=True

app = Flask(__name__)
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'bbs_test'
USERNAME = 'root'
PASSWORD = 'root'

# dialect+driver://username:password@host:port/database
DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8mb4".format(username=USERNAME,password=PASSWORD,host=HOSTNAME,port=PORT,db=DATABASE)

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = '6a8312d499ed42828bb85fefac3607b7'  # CSRF保护设置密钥
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),"static\\uploads")
app.config['PAGE_SET'] = 10  # 分页上限数量
app.config['AUTH_SWITCH'] = False  # 页面访问权限开关，True为开启
#app.config['UP_DIR']=os.getcwd()
#邮件发送
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.163.com')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'emailcheck@163.com')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '1bbsemailcheck')
app.config["MAIL_SERVER"]=MAIL_SERVER
app.config["MAIL_USERNAME"]=MAIL_USERNAME
app.config["MAIL_PASSWORD"]=MAIL_PASSWORD

db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
#migrate = Migrate(app,db)
#manager.add_command('db',MigrateCommand)
moment = Moment()
mail = Mail()
mail.init_app(app)
print("服务器启动时间")
ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print(ts)
print(time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S")))



# user = User(
#     name="name",
#     email="123@163.com",
#     phone="123",
#     pwd=generate_password_hash("12"),
#     uuid=0
# )
# db.session.add(user)
# db.session.commit()

#导入蓝图
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

#注册蓝图
app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint,url_prefix='/admin')





#404
@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html"),404