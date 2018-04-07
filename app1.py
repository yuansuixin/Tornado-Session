# -*- coding:UTF-8 -*-

import tornado.ioloop
import tornado.web
import time
import hashlib


container={
    'asdf':{'k':'v'},
}

class Bar():
    # self，谁调用这个函数，self就是谁
    #这个self就是MainHandler对象，可以将这个self传递给Bar（）
    def __init__(self,handler):
        self.handler = handler
        self.random_str = None
        # 去用户请求信息中获取session_id ，如果没有就是新用户或者是没有登陆
        client_random_str = self.handler.get_cookie('session_id')
        if not client_random_str:
            # 新用户
            self.random_str = self.create_random_str()
            # 添加到数据库中一个数据
            container[self.random_str]={}
        else:
            # 判断是否是合法的session
            if client_random_str in container:
                # 老用户
                self.random_str = client_random_str
            else:
                # 非法用户
                self.random_str = self.create_random_str()
        # 设置更新时间]
        ctime = time.time()
        self.handler.set_cookie('session_id',self.random_str,expires=ctime+1800) # 超时时间



 # 生成随机的字符串,md5摘要
    def create_random_str(self):
        v = str(time.time())
        m = hashlib.md5()
        m.update(bytes(v,encoding='utf-8'))
        return m.hexdigest()


    def __setitem__(self, key, value):
        container[self.random_str][key] = value

    def __getitem__(self, key):
        return container[self.random_str].get(key)
    def __delitem__(self, key):
        del container[self.random_str][key]

    #清空
    def clear(self):
        del container[self.random_str]


class Foo(object):
    def initialize(self):
        self.session = Bar(self)
        super(Foo,self).initialize()



class HomeHandler(Foo,tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        print('home')
        user = self.session['uuuu']
        if not user:
            self.redirect('https://www.baidu.com')
        else:
            self.write(user)



class LoginHandler(Foo,tornado.web.RequestHandler):
    def get(self):
        self.session['uuuu'] = 'root'
        self.redirect('/home')


application = tornado.web.Application([
    (r'/login', LoginHandler),
    (r'/home', HomeHandler),
],)

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
