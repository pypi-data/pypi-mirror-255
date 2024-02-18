#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : fastapi
# @Time         : 2024/1/8 16:05
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

from functools import wraps, partial
from fastapi import HTTPException


def catch_exceptions(func=None, *, exception_type=Exception, status_code=404):
    if func is None:
        return partial(catch_exceptions, exception_type=exception_type, status_code=status_code)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except exception_type as e:
            raise HTTPException(status_code=status_code, detail=f"Error: {e}")

    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exception_type as e:
            raise HTTPException(status_code=status_code, detail=f"Error: {e}")

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()


    @app.get("/test")
    @catch_exceptions(exception_type=IOError, status_code=500)
    def f(file_id: str):
        logger.debug(file_id)
        raise Exception("test")


    app.run(port=9000)
