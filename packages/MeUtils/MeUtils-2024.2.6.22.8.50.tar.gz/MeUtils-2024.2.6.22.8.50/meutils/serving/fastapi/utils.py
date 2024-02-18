#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : utils
# @Time         : 2023/11/28 16:51
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from starlette.requests import Request
from meutils.pipe import *


def get_ipaddr(request: Request) -> str:
    """
    Returns the ip address for the current request (or 127.0.0.1 if none found)
     based on the X-Forwarded-For headers.
     Note that a more robust method for determining IP address of the client is
     provided by uvicorn's ProxyHeadersMiddleware.
    """
    if "X_FORWARDED_FOR" in request.headers:
        return request.headers["X_FORWARDED_FOR"]
    else:
        if not request.client or not request.client.host:
            return "127.0.0.1"

        return request.client.host


def get_remote_address(request: Request) -> str:
    """
    Returns the ip address for the current request (or 127.0.0.1 if none found)
    """
    if not request.client or not request.client.host:
        return "127.0.0.1"

    return request.client.host


def limit(limit_value='3/second', error_message: Optional[str] = None, **kwargs):
    """
        @limit(limit_value='3/minute')
        def f(request: Request):
            return {'1': '11'}
    :return:
    """
    from slowapi.errors import RateLimitExceeded
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
    return limiter.limit(limit_value=limit_value, error_message=error_message, **kwargs)
