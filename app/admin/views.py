#coding:utf8
#调用蓝图
from . import admin

from app import db, app
from app.admin import admin
from flask import render_template, redirect, url_for, flash, session, request, abort
from app.admin.forms import LoginForm,AdminForm,PwdForm
from app.models import Admin, AdminLoginLog,Oplog,User,Comment,Post,UserLoginLog,Col
from functools import wraps
from werkzeug.utils import secure_filename
import os, uuid, datetime
import time

# 定义登录判断装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # session不存在时请求登录
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/')
@admin_login_req
def index():
    print(session['admin']+"进入系统")
    oplog = Oplog(
        type="管理员「%s」进入管理系统" % session["admin"],
        admin_id=session["admin_id"],
        addtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    )
    db.session.add(oplog)
    db.session.commit()
    return render_template("admin/index.html")

# 定义登录视图
@admin.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()  # 导入登录表单
    if form.validate_on_submit():  # 验证是否有提交表单
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for("admin.login"))
        session["admin"] = data["account"]
        session["admin_id"] = admin.id
        adminlog = AdminLoginLog(
            ip=request.remote_addr,
            admin_id = session["admin_id"],
            addtime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        db.session.add(adminlog)
        db.session.commit()
        oplog = Oplog(
            type="管理员「%s」登录管理系统" % session["admin"],
            admin_id = session["admin_id"],
            addtime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


# 定义登出视图
@admin.route("/logout/")
@admin_login_req
def logout():
    admin = session["admin"]
    admin_id = session["admin_id"]
    session.pop("admin")  # 移除用户session
    session.pop("admin_id")
    print(admin+"退出管理系统")
    oplog = Oplog(
        type="管理员「%s」退出管理系统" % admin,
        admin_id = admin_id,
            addtime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    )
    db.session.add(oplog)
    db.session.commit()
    return redirect(url_for("admin.login"))



# 定义添加管理员视图
@admin.route("/admin/add/", methods=["GET", "POST"])
@admin_login_req
def admin_add():
    if session["admin_id"] != 1:
        return redirect(url_for("admin.index"))
    form = AdminForm()
    if form.validate_on_submit():
        data = form.data
        from werkzeug.security import generate_password_hash
        admin = Admin(
            name=data["name"],
            pwd=generate_password_hash(data["pwd"]),
            addtime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        db.session.add(admin)
        db.session.commit()
        flash("添加管理员成功！", "ok")
        oplog = Oplog(
            type="管理员「"+session["admin"]+"」添加新管理员：「%s」" % data["name"],
            admin_id = session["admin_id"],
            addtime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for("admin.admin_add"))
    return render_template("admin/admin_add.html", form=form)


# 定义会员列表视图
@admin.route("/user/list/<int:page>/", methods=["GET"])
@admin_login_req
def user_list(page=None):
    global page_data
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=13)
    return render_template("admin/user_list.html", page_data=page_data)

# 定义查看会员视图
@admin.route("/user/view/<int:id>/", methods=["GET"])
@admin_login_req
def user_view(id=None):
    user = User.query.get_or_404(id)
    page = page_data.page if page_data is not None else 1
    return render_template("admin/user_view.html", user=user, page=page)


# 定义会员删除视图
@admin.route("/user/del/<int:id>/", methods=["GET"])
@admin_login_req
def user_del(id=None):
    if page_data.pages == 1 or page_data is None:
        page = 1
    else:
        page = page_data.page if page_data.page < page_data.pages or page_data.total % page_data.per_page != 1 else page_data.pages - 1
    user = User.query.filter_by(id=id).first_or_404()
    posts = Post.query.filter_by(user_id = id).all()
    comments=Comment.query.filter_by(user_id=id).all()
    cols=Col.query.filter_by(user_id=id).all()
    for col in cols:
        db.session.delete(col)
        db.session.commit()
    for comment in comments:
        db.session.delete(comment)
        db.session.commit()
    for post in posts:
        db.session.delete(post)
        db.session.commit()
    db.session.delete(user)
    db.session.commit()
    if os.path.exists(app.config['UP_DIR'] + "users" + os.sep + str(user.face)):
        os.remove(app.config['UP_DIR'] + "users" + os.sep + str(user.face))
    flash("删除会员成功！", "ok")
    oplog = Oplog(
        type="管理员：「"+session["admin"]+"」 删除会员：「" +user.name+"」",
        admin_id=session["admin_id"]
    )
    db.session.add(oplog)
    db.session.commit()
    return redirect(url_for("admin.user_list", page=page))


# 定义修改密码视图
@admin.route("/pwd/", methods=["GET", "POST"])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        oplog = Oplog(
            admin_id=session["admin_id"],
            type="管理员「"+session["admin"]+"」修改了密码",
            addtime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html", form=form)




# 定义评论列表视图
@admin.route("/comment/list/<int:page>/", methods=["GET"])
@admin_login_req
def comment_list(page=None):
    global page_data
    if page is None:
        page = 1
    # page_data = Comment.query.join(Post).join(User).filter(
    #     Comment.post_id == Post.id,
    #     Comment.user_id == User.id
    # ).order_by(
    #     Comment.addtime.desc()
    # ).paginate(page=page, per_page=app.config['PAGE_SET'])
    #
    page_data = Comment.query.order_by(Comment.addtime.desc()).paginate(page=page, per_page=app.config['PAGE_SET'])
    return render_template("admin/comment_list.html", page_data=page_data)


# 定义评论删除视图
@admin.route("/comment/del/<int:id>/", methods=["GET"])
@admin_login_req
def comment_del(id=None):
    if page_data.pages == 1 or page_data is None:
        page = 1
    else:
        page = page_data.page if page_data.page < page_data.pages or page_data.total % page_data.per_page != 1 else page_data.pages - 1
    comment = Comment.query.filter_by(id=id).first_or_404()
    user = User.query.filter_by(id=comment.user_id).first_or_404()
    post = Post.query.filter_by(id=comment.post_id).first_or_404()
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功！", "ok")
    oplog = Oplog(
        admin_id=session["admin_id"],
        type="管理员「"+session["admin"]+"」删除了会员「%s(id:%s)」在《%s》的评论：%s" % (user.name, user.id, post.title, comment.content),
        addtime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    )
    db.session.add(oplog)
    db.session.commit()
    return redirect(url_for("admin.comment_list", page=page))



# 定义预告列表视图
@admin.route("/preview/list/<int:page>/", methods=["GET", "POST"])
@admin_login_req
def post_list(page=None):
    global page_data
    if page is None:
        page = 1
    page_data = Post.query.order_by(
        Post.addtime.desc()
    ).paginate(page=page, per_page=app.config['PAGE_SET'])
    return render_template("admin/post_list.html", page_data=page_data)


# 定义主题帖删除视图
@admin.route("/preview/del/<int:id>/", methods=["GET"])
@admin_login_req

def post_del(id=None):
    if page_data.pages == 1 or page_data is None:
        page = 1
    else:
        page = page_data.page if page_data.page < page_data.pages or page_data.total % page_data.per_page != 1 else page_data.pages - 1
    post = Post.query.filter_by(id=id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    oplog = Oplog(
        admin_id=session["admin_id"],
        type="管理员「"+session["admin"]+"」删除了主题帖：《%s》" % post.title,
        addtime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    )
    db.session.add(oplog)
    db.session.commit()
    return redirect(url_for("admin.post_list", page=page))


# 定义操作日志列表视图
@admin.route("/oplog/list/<int:page>/", methods=["GET"])
@admin_login_req
def oplog_list(page=None):
    global page_data
    if page is None:
        page = 1
    page_data = Oplog.query.join(Admin).filter(
        Oplog.admin_id == Admin.id
    ).order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=app.config['PAGE_SET'])
    return render_template("admin/oplog_list.html", page_data=page_data)


# 定义管理员登录日志列表视图
@admin.route("/adminloginlog/list/<int:page>/", methods=["GET"])
@admin_login_req
def adminloginlog_list(page=None):
    global page_data
    if page is None:
        page = 1
    page_data = AdminLoginLog.query.join(Admin).filter(
        AdminLoginLog.admin_id == Admin.id
    ).order_by(
        AdminLoginLog.addtime.desc()
    ).paginate(page=page, per_page=app.config['PAGE_SET'])
    return render_template("admin/adminloginlog_list.html", page_data=page_data)


# 定义会员登录日志列表视图
@admin.route("/userloginlog/list/<int:page>/", methods=["GET"])
@admin_login_req
def userloginlog_list(page=None):
    global page_data
    if page is None:
        page = 1
    page_data = UserLoginLog.query.join(User).filter(
        UserLoginLog.user_id == User.id
    ).order_by(
        UserLoginLog.addtime.desc()
    ).paginate(page=page, per_page=app.config['PAGE_SET'])
    return render_template("admin/userloginlog_list.html", page_data=page_data)