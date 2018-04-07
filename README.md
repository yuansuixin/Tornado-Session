---
title: 使用Tornado自定义Session组件
date: 2018-04-05 22:02:18
tags:
---


最近又看了看tornado框架，写了一个自定义的组件。一直没时间上传，今天终于可以和大家见面了，对了，大家在和本文亲密之前需要先预热一下哦~:stuck_out_tongue::stuck_out_tongue::stuck_out_tongue:

[预热](https://yuansuixin.github.io/2018/03/30/tornado-session-py/ "预热")


## Tornado的自定义session组件

#### 1. session会话技术

- 既然咱们要说一说session，那么必然要知道session是什么，接下来让我们一同了解一下session吧！

    - Session 是服务器保存的一个数据结构，用来跟踪用户的状态，这个数据可以保存在集群、数据库、文件中
    - Cookie 是客户端保存用户信息的一个机制，用来记录用户的一些信息，也是实现Session的一个方式，存储在用户的浏览器中

    [cookie和session会话技术详细讲解](https://yuansuixin.github.io/2018/02/12/cookie-session/ "cookie和session会话技术详细讲解")

#### 2. 自定义session原理解析

我们先来看看tornado的基础程序

```
# -*- coding:UTF-8 -*-
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello world')

settings = {
    'template_path': 'views',
}

application = tornado.web.Application([
    (r'/index', MainHandler),
], **settings)

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```

- 我们会发现当请求来的时候，就会调用get()方法，那么大家想一下，这个get()方法的调用是不是需要MainHandler对象来调用，如果没有对象，MainHandler里面的get()根本就调用不了，

- 所以肯定是要先创建对象，要创建对象那么一定要执行``__init__()``方法，然而我们没有写``__init__()``方法，那怎么办呢，这时候我们准备的知识点就用到啦，需要到父类中去查找，也就是RequestHandler类的``__init__()``,
- 我们可以看到RequestHandler类的``__init__()``，也就是说，在调用这个get（）方法之前肯定要调用``__init__()``方法，也就是说只要在``__init__()``方法中写入的东西都是get（）或者post（）方法之前的。
- 我们可以发现在``__init__()``方法的最后调用了 ``self.initialize(**kwargs)``然而，这个方法什么都没写，也就是给我们预留的添加自己的操作的方法，我们将从这里入手

- 通过继承的机制我们可以知道要向给handler添加自己的东西，有两种写法

```
第一种：多继承
class Foo(object):
    def initialize(self):
        self.A = 123
        super(Foo,self).initialize()
class MainHandler(Foo,tornado.web.RequestHandler):
    def get(self):
        print(self.A)
        self.write('hello world')
第二种：常规写法
class Foo(tornado.web.RequestHandler):
    def initialize(self):
        self.A = 123
        super(Foo,self).initialize()
class MainHandler(Foo):
    def get(self):
        print(self.A)
        self.write('hello world')
```
> 因为Python是支持多继承的，所以我们将以多继承的这种方式进行解析

- 我们模拟Django的session来说，登录账号之后，session就自动的帮我们写到了服务器上了，我们要开源这个组件就需要让用户感知起来非常的方便，所以，我们以后就想让用户这样写

```
self.session['xxx'] = 'dfdafdasfd'
```

- 所以我们需要做这些事情，而且我们需要【】这样取值，我们首先想到的类型就是字典，没错，字典是这样取值，但是我们提前的知识点可不是白学的呦，使用``__setitem__()``魔法方法就可以呦，为了后面的额步骤,我们选择可以使用类。
    1. 生成随机字符串
    2. 写到用户cookie
    3. 后台存储

- 大家应该还记得MainHandler里面有self.set_cookie()函数，我们需要使用这个函数将session_id 写入cookie中，然而Foo类中的self就是MainHandler对象，所以我们只需要将self传入Bar就可以了

- 将session写入数据库，我们先使用一个字典充当数据库


#### 3. 写自定义的session代码

- 我们按照我们分析的原理将代码写出来

```
# -*- coding:UTF-8 -*-

import tornado.ioloop
import tornado.web
import time
import hashlib

# 存储session数据
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

```


#### 4. 存储session

- 我们将session放到了一个字典里，只是放到了内存里，然而我们不想放内存里怎么办呢？为了提高用户的需求的灵活性，我们可以将存储使用类实现，使其可以放入缓存，内存，数据库等你想放的地方

```
# -*- coding:UTF-8 -*-

import tornado.ioloop
import tornado.web
import time
import hashlib

class Cache(object):
    def __int__(self):
        self.container = {}
    def __contains__(self, item):
        return  item in self.container
    def open(self):
        pass
    def initial(self,random_str):
        self.container[random_str] = {}
    def close(self):
        pass
    def get(self,random_str,key):
        self.container[random_str].get(key)
    def set(self,random_str,key,value):
        self.container[random_str][key] = value
    def delete(self,random_str,key):
        del self.container[random_str][key]
    def clear(self,random_str,):
        del self.container[random_str]

class Memcache(object):
    def __int__(self):
        self.container = {}
    # 适用性更广考虑才加上的open（）和close（）函数，更严谨
    def open(self):
        pass

    def close(self):
        pass
    def get(self):
        pass
    def set(self):
        pass
    def delete(self):
        pass

# 是为了方便更换，想放入什么里面直接更改这个引用就可以
P = Cache

class Session():
    # self，谁调用这个函数，self就是谁
    #这个self就是MainHandler对象，可以将这个self传递给Bar（）
    def __init__(self,handler):
        self.handler = handler
        self.random_str = None
        self.ppp = P()
        self.ppp.open()

        # 去用户请求信息中获取session_id ，如果没有就是新用户或者是没有登陆
        client_random_str = self.handler.get_cookie('session_id')
        if not client_random_str:
            # 新用户
            self.random_str = self.create_random_str()
            # 添加到数据库中一个数据
            self.ppp.initial(self.random_str)
        else:
            # 判断是否是合法的session
            if client_random_str in self.ppp:
                # 老用户
                self.random_str = client_random_str
            else:
                # 非法用户
                self.random_str = self.create_random_str()
                # 添加一个数据
                self.ppp.initial(self.random_str)
        # 设置更新时间
        ctime = time.time()
        self.handler.set_cookie('session_id',self.random_str,expires=ctime+1800) # 超时时间
        self.ppp.close()


 # 生成随机的字符串,md5摘要
    def create_random_str(self):
        v = str(time.time())
        m = hashlib.md5()
        m.update(bytes(v,encoding='utf-8'))
        return m.hexdigest()


    def __setitem__(self, key, value):
        self.ppp.open()
        self.ppp.set(self.random_str,key,value)
        self.ppp.close()

    def __getitem__(self, key):
        self.ppp.open()
        v = self.ppp.get(self.random_str,key)
        self.ppp.close()
        return v
    def __delitem__(self, key):
        self.ppp.open()
        self.ppp.delete(self.random_str,key)
        self.ppp.close()

    #清空
    def clear(self):
        self.ppp.open()
        self.ppp.clear(self.random_str,)
        self.ppp.close()


class Foo(object):
    def initialize(self):
        self.session = Session(self)
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

```

- 这样我们的自定义session会话就完成啦，快快使用一下吧！:yum:


> 有什么不正确的地方欢迎指点哟！:kissing_heart:
> 邮箱：cyss428@163.com


