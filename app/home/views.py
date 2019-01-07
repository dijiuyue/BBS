# coding:utf8
# 调用蓝图
from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegistForm, LoginForm, UserdetailForm, PwdForm, CommentForm, PostForm
from app.models import User, UserLoginLog, Comment, Post,Col
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import uuid
from app import db,app,mail
from app.home.email import send_mail
from functools import wraps
import time
import os


# 定义用户登录判断装饰器
def user_login_req(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # session不存在时请求登录
        if "user" not in session:
            return redirect(url_for("home.user_login", next=request.url))
        return func(*args, **kwargs)

    return decorated_function


# html测试路由
@home.route('/usefortest/')
def ust():
    return render_template('home/USERFORTEST.html')


# 首页路由
@home.route('/')
def index():
    # posts = Post.query.all()
    current_user_id = 0
    current_user_name =""
    if "user" in session:
        current_user_id = session["user_id"]
        current_user_name = session["user"]

    page_index = request.args.get('page', 1, type=int)
    query = Post.query.join(User).filter(User.id == Post.user_id).order_by(Post.addtime.desc())
    pagination = query.paginate(page_index, per_page=10, error_out=False)
    posts = pagination.items
    return render_template('home/index.html', posts=posts, pagination=pagination,current_user_name=current_user_name,current_user_id=current_user_id)
#首页删除个人发布的内容
@home.route("/index/del/")
@user_login_req
def index_del():
    #获取当前登录用户id
    current_user_id = session["user_id"]
    index_id = request.args.get("id", '0')
    post = Post.query.get_or_404(int(index_id))
    if post.user_id != current_user_id:
        flash("删除不合法")
        return redirect(url_for("home.index"))
    db.session.delete(post)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("home.index"))


#设置帖子关注
@home.route("/index/col/")
@user_login_req
def index_col():
    #获取当前登录用户id
    current_user_id = session["user_id"]
    index_id = request.args.get("id", '0')
    col_check = Col.query.filter_by(id=index_id).count()
    if col_check == 0:
        col=Col(
            post_id=index_id,
            user_id=current_user_id
        )
        db.session.add(col)
        db.session.commit()
        flash("收藏成功","ok")
    flash("收藏已存在","err")
    return redirect(url_for("home.index"))


#设置评论关注
@home.route("/play/col/")
@user_login_req
def play_col():
    #获取当前登录用户id
    current_user_id = session["user_id"]
    index_id = request.args.get("id", '0')
    col_check = Col.query.filter_by(id=index_id).count()
    if col_check == 0:
        col=Col(
            comment_id=index_id,
            user_id=current_user_id
        )
        db.session.add(col)
        db.session.commit()
        flash("收藏成功","ok")
    flash("收藏已存在","err")
    return redirect(url_for("home.index"))


#
# from io import BytesIO
# from . import verify_code
# @home.route('/code')
# def get_code():
#     image, code = verify_code.get_verify_code()
#     # 图片以二进制形式写入
#     buf = BytesIO()
#     image.save(buf, 'jpeg')
#     buf_str = buf.getvalue()
#     # 把buf_str作为response返回前端，并设置首部字段
#     response = verify_code.make_response(buf_str)
#     response.headers['Content-Type'] = 'image/gif'
#     # 将验证码字符串储存在session中
#     session['image'] = code
#     return response

@home.route('/activate/<token>')
def activate(token):
    #验证token 提取id
    if User.check_active_token(token):
        flash("账户已经激活")
        return redirect(url_for("home.user_login"))
    else:
        flash("激活失败")
        return redirect(url_for("home.index"))

# 登录路由
@home.route("/login/", methods=["POST", "GET"])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        # if session.get('image').lower() != form.verify_code.data.lower():
        #     flash('验证码错误')
        #     return render_template('home/user_login.html', form=form)
        print("用户激活状态"+str(user.activate))
        if  user.activate:
            if not user.check_pwd(data["pwd"]):
                flash("用户名或密码错误！")
                return redirect(url_for("home.user_login"))
            session["user"] = data["name"]
            session["user_id"] = user.id
            userloginlog = UserLoginLog(
            user_id=user.id,
            ip=request.remote_addr,
            addtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            )
            db.session.add(userloginlog)
            db.session.commit()
            return redirect(request.args.get('next') or url_for("home.index"))
        else:
            flash("用户尚未激活,请激活以后再登录")
    return render_template('home/user_login.html', form=form)


# 登出路由
@home.route("/logout/")
@user_login_req
def logout():
    session.pop("user")
    session.pop("user_id")
    return redirect(url_for("home.user_login"))


# 会员注册
@home.route("/register/", methods=['GET', "POST"])
def register():
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex,
            addtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        print(user)
        check = User.query.filter_by(name=data["name"]).count()
        if check == 0:
            db.session.add(user)
            db.session.commit()
            print("用户数据提交到数据库")
            token = user.generate_active_token()
            # 发送用户账户激活的邮件
            send_mail(user.email, '激活您的账户', 'email/activate', username=user.name, token=token)
            # 弹出消息 提示用户
            flash("注册成功，请点击邮件中的链接完成激活")
            return redirect(url_for("home.user_login"))
        flash("用户名已存在")
    return render_template('home/register.html', form=form)

# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)  # 对名字进行前后缀分离
    #注意此处datetime.now()
    filename = time.strftime("%Y%m%d%H%M%S") + "_"  + fileinfo[-1]  # 生成新文件名
    return filename

# 用户中心
@home.route("/user/", methods=["GET", "POST"])
@user_login_req
def user():
    form = UserdetailForm()
    user = User.query.get(int(session["user_id"]))
    if user.face is not None:
        form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        print('button pressed')
        data = form.data
        # if data["name"] != user.name and name_count == 1:
        #     flash("用户名已被占用")
        #     return redirect(url_for("home.user"))
        if request.method == 'POST':
            file = request.files['file']
            print("获取文件成功")
            filename = secure_filename(str(hash(file.filename)))+session["user"]+".jpg"
            print("secure成功"+filename)
            del_face = user.face
            file.save(os.path.join(app.config['UP_DIR']  + os.sep+"users", filename))
            #os.remove(os.path.join(app.config['UP_DIR']  + os.sep+"users", del_face))
            print("删除文件"+del_face+"成功")
            user.face = filename
        user.name=data["name"]
        user.email=data["email"]
        user.phone=data["phone"]
        user.info=data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功！")
        return redirect(url_for("home.user"))
    flash("失败")
    return render_template('home/user.html', form=form, user=user)


@home.route("/pwd/", methods=["GET", "POST"])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=session["user"]).first()
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for("home.logout"))
    return render_template('home/pwd.html', form=form)


# 会员中心评论列表 评论功能在paly路由中
@home.route("/comments/")
@user_login_req
def comments():
    user_id = session["user_id"]
    user=User.query.filter_by(id=user_id).first()
    user_name = session["user"]
    page = request.args.get('page', 1, type=int)
    # query = Comment.query.order_by(Comment.addtime.desc())
    query = Comment.query.filter(Comment.user_id == user_id).order_by(Comment.addtime.desc())
    pagination = query.paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('home/comments.html', user=user,user_name=user_name, comments=comments,pagination=pagination)


@home.route("/comments/del/")
@user_login_req
def comment_del():
    comment_id = request.args.get("id", '')
    comment = Comment.query.get_or_404(int(comment_id))
    db.session.delete(comment)
    db.session.commit()
    flash("评论删除成功")
    return redirect(url_for("home.comments"))


@home.route("/postrecords/")
@user_login_req
def postrecords():
    user_id = session["user_id"]
    user_name = session["user"]
    user = User.query.filter_by(id=user_id).first()
    page = request.args.get('page', 1, type=int)
    # query = Comment.query.order_by(Comment.addtime.desc())
    query = Post.query.filter(Post.user_id == user_id).order_by(Post.addtime.desc())
    pagination = query.paginate(page, per_page=5, error_out=False)
    posts = pagination.items
    return render_template('home/post_records.html', user=user,user_name=user_name, posts=posts, pagination=pagination)

@home.route("/postrecords/del/")
@user_login_req
def post_del():
    post_id = request.args.get("id", '')
    post = Post.query.get_or_404(int(post_id))
    comment = Comment.query.filter_by(post_id=post_id).all()

    db.session.delete(post)
    db.session.commit()
    db.session.delete(comment)
    db.session.commit()
    flash("主题帖删除成功")
    return redirect(url_for("home.postrecords"))


@home.route("/loginlog/", methods=["POST", "GET"])
@user_login_req
def loginlog():
    user_login_log = UserLoginLog.query.filter_by(
        user_id=session["user_id"]

    ).order_by(
        UserLoginLog.addtime.desc()
        # 此处限制了查寻到的登录日志为前15条
    ).limit(15).all()
    return render_template("home/loginlog.html", user_login_log=user_login_log)

@home.route("/col/del/")
@user_login_req
def col_del():
    current_user_id = session["user_id"]
    col_id = request.args.get("id", '')
    col = Col.query.get_or_404(int(col_id))
    if col.user_id != current_user_id:
        flash("收藏删除不合法")
        return redirect(url_for("home.col"))
    db.session.delete(col)
    db.session.commit()
    flash("收藏删除成功")
    return redirect(url_for("home.col"))


##会员中心收藏列表
@home.route("/col/")
@user_login_req
def col():
    user_id = session['user_id']
    # 获取当前分页页面编号（编号，默认值，类型）
    page = request.args.get('page', 1, type=int)
    # 从数据库中查找对应用户的收藏
    #query =Col.query.filter_by(user_id =user_id).order_by(Col.addtime.desc())
    query = Col.query.join(Post).join(User).filter(Col.user_id==user_id,Col.post_id == Col.post_id).order_by(Col.addtime.desc())
    # 对当前贴的评论进行分页（分页号，每页展示的数量，error）
    pagination = query.paginate(page, per_page=5, error_out=False)
    # 获得分页后当前页显示的评论
    cols = pagination.items
    # 渲染主题帖展示页面
    print(query)
    return render_template('home/col.html',cols=cols,pagination=pagination)


@home.route("/index/")
def reindex():  # z此处index重复
    return redirect(url_for("home.index"))


@home.route('/animation/')
def animation():
    data = {'sgd.jpg', 'sutstudent.jpg', 'sutsight01.jpg', 'sutsight02.jpg', 'hxxy.jpg'}
    return render_template('home/animation.html', data=data)


@home.route('/search/')
def search():
    current_user_id = 0
    current_user_name = ""
    if "user" in session:
        current_user_id = session["user_id"]
        current_user_name = session["user"]
    # 获取查询的内容
    # search=request.args.get("search",'',type=str)
    search = request.args.get("search", "搜索结果为空")
    # print("搜索的的内容"+search)
    # 获取当前分页页面编号（编号，默认值，类型）
    page = request.args.get('page', 1, type=int)
    # 从数据库中查找对应当前主题贴的评论
    query = Post.query.filter(Post.title.ilike('%' + search + '%')).order_by(Post.addtime.desc())
    # 对当前主题帖的评论数量进行统计
    post_count = Post.query.filter(Post.title.ilike('%' + search + '%')).count()
    # 对当前贴的评论进行分页（分页号，每页展示的数量，error）

    pagination = query.paginate(page, per_page=5, error_out=False)
    # 获得分页后当前页显示的评论
    comments = pagination.items
    # 渲染主题帖展示页面
    return render_template("home/search.html", search=search, count=post_count, current_user_name=current_user_name,pagination=pagination, results=comments,current_user_id=current_user_id)


# 主题帖详情页
@home.route('/play/', methods=["GET", "POST"])
def play():
    # 从请求参数拿到请求的post_id
    post_id = request.args.get("post_id", "")
    # 评论表单
    form = CommentForm()
    # 清除表单内容
    form.data['content'] = ""
    # 利用post_id找到要显示的主题贴
    post = Post.query.filter(Post.id == post_id).first()
    # 利用post_id在User表中查找作者姓名
    author = User.query.filter(User.id == post.user_id).first()
    # 从session中取得当前登陆中的用户名
    current_user_id = 0
    current_user_name = '游客'
    if "user" in session:
        current_user_name = session["user"]
        current_user_id= session["user_id"]
    # 若用户登录则显示评论发布表单
    if "user" in session and form.validate_on_submit():
        comment = Comment(
            content=form.data["content"],
            post_id=int(post_id),
            user_id=session["user_id"],
            addtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        db.session.add(comment)
        db.session.commit()
        flash("评论提交成功！")
    # 获取当前分页页面编号（编号，默认值，类型）
    page = request.args.get('page', 1, type=int)
    # 从数据库中查找对应当前主题贴的评论
    query = Comment.query.join(User).filter(Comment.post_id == post_id).order_by(Comment.addtime.desc())
    # 对当前主题帖的评论数量进行统计
    comment_count = Comment.query.filter(Comment.post_id == post_id).count()
    # 对当前贴的评论进行分页（分页号，每页展示的数量，error）
    pagination = query.paginate(page, per_page=5, error_out=False)
    # 获得分页后当前页显示的评论
    comments = pagination.items
    # 渲染主题帖展示页面
    return render_template("home/play.html", post=post, form=form, comments=comments,
                           pagination=pagination, author=author,current_user_name=current_user_name, count=comment_count,current_user_id=current_user_id)


@home.route('/post/', methods=["GET", "POST"])
@user_login_req
def post():
    form = PostForm()
    current_user_name = session["user"]
    if form.validate_on_submit():
        data = form.data
        post = Post(
            title=data["title"],
            content=data["content"],
            user_id=session["user_id"],
            addtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        db.session.add(post)
        db.session.commit()
        flash("发布主题帖成功")
    return render_template("home/post_add.html", form=form,current_user_name=current_user_name)
