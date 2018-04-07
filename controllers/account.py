# -*- coding:UTF-8 -*-
from tornado import web
import tornado

class LoginHandler(tornado.web.RequestHandler):
    def get(self,*args,**kwargs):

        # 如果post要传递参数则，get里也必须要传参，这个和Django不同
        self.render('login.html',msg='')


    def post(self,*args,**kwargs):
        username = self.get_argument('username')
        pwd = self.get_argument('password')
        print(username,pwd)
        if username=='root' and pwd=='1234':
            # self.set_cookie('xxx','ooo')
            self.set_secure_cookie('xxx','ooo')
            self.redirect('/home')
        else:
            self.render('login.html',msg='用户名或者密码错误')










