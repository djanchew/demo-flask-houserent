from wtforms import Form, StringField, FloatField
from wtforms.validators import Length, NumberRange, EqualTo, Email


class RegisterValidate(Form):
    username = StringField(validators=[Length(min=1, max=20, message='长度介于1到20')])
    phone = StringField(validators=[Length(min=11, max=11, message='长度等于11')])
    email = StringField(validators=[Email(message='邮箱格式不正确')])
    password = StringField(validators=[Length(min=3, max=16, message='长度介于3到16')])
    re_password = StringField(
        validators=[Length(min=3, max=16, message='长度介于3到16'), EqualTo('password', message='两次密码不一致')])
