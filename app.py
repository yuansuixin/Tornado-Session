# -*- coding:UTF-8 -*-

import tornado.ioloop
import tornado.web

from controllers.account import LoginHandler
from controllers.home import HomeHandler

import UImethod
import uimodules

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello world')


settings = {
    'template_path': 'views',
    'cookie_secret':'adfsafdsgfsdgdsfgfd',
    'ui_methods': UImethod,
    'ui_modules':uimodules,
    'static_path':'static',
}

application = tornado.web.Application([
    (r'/index', MainHandler),
    (r'/login', LoginHandler),
    (r'/home', HomeHandler),
], **settings)

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
