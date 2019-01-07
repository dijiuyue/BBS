from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin


class LoginForm(FlaskForm):
    """管理员登录表单"""
    account = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={  # 附加选项
            "class": "form-control",
            "placeholder": "请输入账号！",
            # "required": "required"  # 添加强制属性，H5会在前端验证
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            # "required": "required"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat -align-center"

        }
    )

    # 账号验证
    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在！")


class AdminForm(FlaskForm):
    """管理员表单"""
    name = StringField(
        label="管理员名称",
        validators=[
            DataRequired("请输入管理员名称！")
        ],
        description="管理员名称",
        render_kw={  # 附加选项
            "class": "form-control",
            "autofocus": "",
            "placeholder": "请输入账号！"
        }
    )
    pwd = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("请输入管理员密码！")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码！"
        }
    )
    re_pwd = PasswordField(
        label="管理员重复密码",
        validators=[
            DataRequired("请再次输入管理员密码！"),
            EqualTo('pwd', message="两次密码输入不一致！")
        ],
        description="管理员重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请再次输入管理员密码！"
        }
    )

    submit = SubmitField(
        '提交',
        render_kw={
            "class": "btn btn-primary"
        }
    )

    def validate_name(self, field):
        auth = Admin.query.filter_by(name=field.data).count()
        if auth == 1:
            raise ValidationError("管理员名称已经存在！")



class PwdForm(FlaskForm):
    """修改密码"""
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "autofocus": "",
            "placeholder": "请输入旧密码！"
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
        label="再次输入新密码",
        validators=[
            DataRequired("请再次输入新密码！"),EqualTo("new_pwd","两次输入的密码不一致")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请再次输入新密码！"
        }
    )

    submit = SubmitField(
        '提交',
        render_kw={
            "class": "btn btn-primary"
        }
    )

    # 旧密码验证
    def validate_old_pwd(self, field):
        from flask import session
        old_pwd = field.data
        name = session["admin"]
        admin = Admin.query.filter_by(name=name).first()
        if not admin.check_pwd(old_pwd):
            raise ValidationError("旧密码错误！")
