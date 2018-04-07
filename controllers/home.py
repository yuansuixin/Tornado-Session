# -*- coding:UTF-8 -*-
import tornado
from tornado import web

class HomeHandler(tornado.web.RequestHandler):
    # tornado的get方法不需要返回，如果想让后面的代码不执行，直接return就可以
    def get(self):
        xxx = self.get_secure_cookie('xxx')
        if not xxx:
            self.redirect('/login')
            return
        self.write('欢迎回家')






