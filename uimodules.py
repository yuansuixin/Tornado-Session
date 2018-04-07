# -*- coding:UTF-8 -*-
from tornado.web import UIModule


class Custom(UIModule):
    # 渲染内容
    def render(self, *args, **kwargs):
        print(args,kwargs)
        return '老村长'

    def embedded_css(self):
        return '.c1{display:none}'
# 引入css，js文件
    def css_files(self):
        return 'fdsaf'
    def javascript_files(self):
        return 'fafdsaf'
    def embedded_javascript(self):
        return 'fdasfda'


