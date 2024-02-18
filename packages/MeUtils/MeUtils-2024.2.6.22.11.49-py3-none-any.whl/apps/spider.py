#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : spider
# @Time         : 2024/1/18 12:09
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from meutils.serving.fastapi import App
from meutils.serving.fastapi.routers import spider

app = App()

# 预览版
app.include_router(spider.router, '/preview/spider')

if __name__ == '__main__':
    app.run(port=39666)
