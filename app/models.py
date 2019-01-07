# coding:utf8
import time
from app import db
from itsdangerous import  TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

# 会员
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码
    email = db.Column(db.String(100), unique=True)  # 邮箱
    phone = db.Column(db.String(11), unique=True)  # 手机号码
    info = db.Column(db.Text)  # 个性简介
    face = db.Column(db.String(255), default="default.jpg")  # 头像
    addtime = db.Column(db.String(30), index=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 注册时间
    uuid = db.Column(db.String(255), unique=True)  # 唯一标识符t
    activate = db.Column(db.BOOLEAN,default=False)
    # userlogs = db.relationship('Userlog', backref='user')  # 会员日志外键关系关联
    comments = db.relationship('Comment', backref='user')  # 评论外键关系关联
    cols = db.relationship('Col', backref='user')  # 收藏外键关系关联
    user_login_log = db.relationship('UserLoginLog', backref='user')
    posts = db.relationship('Post', backref='user')

    def __repr__(self):
        return "<User %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)  # 验证密码是否正确，返回True和False
    def generate_active_token(self,expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expires_in)
        return s.dumps({'id':self.id})
    #检测账户激活的token
    def check_active_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        #data.get('id') 这是从token中获取id 知道是谁点击了激活
        user = User.query.get(data.get('id'))
        #根据这个id 从数据库里查询
        if not user:
            #print("用户不存在")
            return False
        if not user.activate: #如果该用户没有激活 那么激活
            user.activate =True
            db.session.add(user)
            db.session.commit()
            #print("用户激活成功")
        return True
    #print("用户激活失败")


# 会员评论日志
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)
    addtime = db.Column(db.String(30), index=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 评论时间
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    cols = db.relationship('Col', backref='comments')  # 收藏外键关系关联

    def __repr__(self):
        return "<Comment %r>" % self.id


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    addtime = db.Column(db.String(30), index=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 发帖时间
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship('Comment', backref='posts')  # 评论外键关系关联
    cols = db.relationship('Col', backref='posts')  # 收藏外键关系关联

    # user = db.relationship("User",backref=db.backref('posts'))

    def __repr__(self):
        return "<Post %r>" % self.name


# 收藏
class Col(db.Model):
    __tablename__ = "cols"
    id = db.Column(db.Integer, primary_key=True)  # 收藏编号
    addtime = db.Column(db.String(30), index=True,
                        default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 时间  # 收藏时间
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    def __repr__(self):
        return "<Col %r>" % self.id


# 管理员
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)  # 管理员编号
    addtime = db.Column(db.String(30), index=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 时间
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码
    oplog_id = db.relationship('Oplog', backref='oplogs')  # 收藏外键关系关联
    admin_login_log = db.relationship('AdminLoginLog', backref='admin')

    def __repr__(self):
        return "<Admin %r>" % self.title

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)  # 验证密码是否正确，返回True和False


# 操作日志
class Oplog(db.Model):
    __tablename__ = "oplogs"
    id = db.Column(db.Integer, primary_key=True)  # 管理员编号
    addtime = db.Column(db.String(30), index=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 时间
    type = db.Column(db.String(20))
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))

    def __repr__(self):
        return "<Oplog %r>" % self.type


# 用户登录日志
class UserLoginLog(db.Model):
    __tablename__ = "user_login_log"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    addtime = db.Column(db.String(30), index=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 时间
    ip = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<UserLoginLog %r>" % self.id


# 管理员登录日志
class AdminLoginLog(db.Model):
    __tablename__ = "admin_login_log"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    addtime = db.Column(db.String(30), index=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    ip = db.Column(db.String(20))
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))

    def __repr__(self):
        return "< AdminLoginLog %r>" % self.name

# db.drop_all()
# print("删除成功")
# db.create_all()
# print("创建数据库成功")
