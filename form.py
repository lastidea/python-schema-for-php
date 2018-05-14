from flask.ext.wtf import Form                #导入Form类
from wtforms import StringField, BooleanField   #导入文本输入框，导入Boolean选择框，这个Boolean框就是打钩或者不打勾的功能
from wtforms.validators import DataRequired    #导入数据验证功能

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])  #定义LoginForm类，有2个属性，第一个openid，是一个文本输入框
    remember_me = BooleanField('remember_me', default=False)    #第二个remember_me是一个勾选框，告诉系统要不要勾选，默认不勾选