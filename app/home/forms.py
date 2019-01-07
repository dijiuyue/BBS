# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,TextAreaField,FileField
from wtforms.validators import DataRequired, EqualTo, Email,  ValidationError,Regexp
from app.models import User

class RegistForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[DataRequired("请输入昵称")],
        description="昵称",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入昵称",
        }
    )

    email = StringField(
        label="邮箱",
        validators=[DataRequired("请输入邮箱"), Email('邮箱格式不正确')],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入邮箱",
        }
    )

    phone = StringField(
        label="手机",
        validators=[DataRequired("请输入手机"), ],
        description="手机",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入手机",
        }
    )

    pwd = PasswordField(
        label="密码",
        validators=[DataRequired("请输入密码")],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码",
        }
    )

    repwd = PasswordField(
        label="确认密码",
        validators=[DataRequired("请在次输入密码"), EqualTo('pwd', message='两次输入密码不一致！')],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请在次输入密码",
        }
    )
    submit = SubmitField(
        label='注册',
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

def validate_name(self,field):
    name = field.data
    user = User.query.filter_by(name=name).count()
    if user == 1:
        return ValidationError("昵称已存在")


class LoginForm(FlaskForm):
    """会员登录表单"""
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入账号！",
            "autofocus": ""
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！"
        }
    )
    verify_code = StringField(
        label='验证码',
        validators=[
            DataRequired("请输入验证码")
        ],
        description="验证码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入验证码！"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-lg btn-primary btn-block"
        }
    )

    # 账号验证
    def validate_name(self, field):
        name = field.data
        if User.query.filter_by(name=name).count() == 0:
            raise ValidationError("账号不存在！")

class UserdetailForm(FlaskForm):
    """会员中心表单"""
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称！")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入昵称！",

        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱！"),
            Email("邮箱格式不正确！")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱！"
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机号码！"),
            Regexp("^1[3|4|5|7|8][0-9]{9}$", message="手机号码格式不正确！")
        ],
        description="手机",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机号码！"
        }
    )
    face = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像！")
        ],
        description="头像",
        render_kw={
            "id": "input_face"
        }
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 10,
            "autofocus": ""
        }
    )
    submit = SubmitField(
        label='修改',
        render_kw={
            "class": "btn  btn-success"
        }
    )

 #   """修改密码"""
class PwdForm(FlaskForm):

    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
            "autofocus": ""
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码！")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！"
        }
    )
    renew_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请再次输入新密码！"),EqualTo('new_pwd',"两次输入的新密码不一致")
        ],
        description="再次输入新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请再次输入新密码！"
        }
    )
    submit = SubmitField(
        '修改密码',
        render_kw={
            "class": "btn btn-success"
        }
    )

    # 旧密码验证
    def validate_old_pwd(self, field):
        from flask import session
        old_pwd = field.data
        name = session["user"]
        user = User.query.filter_by(name=name).first()
        if not user.check_pwd(old_pwd):
            raise ValidationError("旧密码错误！")

class PostForm(FlaskForm):
    title = StringField(
        label="标题",
        validators=[
            DataRequired('请输入文章标题')
        ],
        description = "标题",
            render_kw={
                "class": "form-control",
                "rows": 5,
                #"autofocus": ""
            }
    )
    #这里用了一个flask_pagedown.filed的PagedownFiled 可能无法被渲染
    content = TextAreaField(
        label="正文内容",
        validators=[
            DataRequired("请输入正文内容")
        ],
        description="正文内容",
        render_kw={
            "class": "form-control",
             "rows": 16,
             "placeholder":"请自觉遵守互联网相关的政策法规，严禁发布色情、暴力、反动的言论。"
            # "autofocus": ""
        }
    )
    submit = SubmitField(
        "发表",
        render_kw = {
             "class": "btn btn-success",
             "href":"{{ url_for('home.index')}}"
        }
    )

class CommentForm(FlaskForm):
    content = TextAreaField(
        label="评论内容",
        validators=[
            DataRequired("请输入评论内容")
        ],
        description="评论内容",
        render_kw={
            "class":"ipt-txt",
            "id":"form-control",
            "rows": 2,
            "cols":133,
            "placeholder":"请自觉遵守互联网相关的政策法规，严禁发布色情、暴力、反动的言论。"
        }
    )
    submit = SubmitField(
        "发布评论",
        render_kw={
            "class":"comment-submit" ,
            "id":"btn-sub",
            "action":"{{ url_for('home.play')}}?post_id={{ post.id }}"
        }
    )

class ColForm(FlaskForm):
    "收藏'",
    submit = render_kw={
            "class":"btn btn-success" ,
            "id":"btn-sub",
            "action":"{{ url_for('home.play')}}?post_id={{ post.id }}"
        }
