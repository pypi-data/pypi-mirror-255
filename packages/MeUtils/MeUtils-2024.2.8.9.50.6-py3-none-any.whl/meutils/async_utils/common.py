#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : common
# @Time         : 2023/8/25 18:44
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

import inspect
import asyncio
from typing import Coroutine

from async_lru import alru_cache
from asgiref.sync import sync_to_async


def arun(coroutine: Coroutine, debug=None):
    return asyncio.run(coroutine, debug=debug)


def aclose():
    import nest_asyncio
    nest_asyncio.apply()


def close_event_loop():
    import nest_asyncio
    nest_asyncio.apply()


def async2sync_generator(generator):
    """
        async def async_generator():
            for i in range(10):
                await asyncio.sleep(1)
                yield i

        # 使用同步生成器
        for item in async2sync_generator(range(10)):
            print(item)
    :param generator:
    :return:
    """
    if inspect.isasyncgen(generator):
        # close_event_loop()
        while 1:
            try:
                yield asyncio.run(generator.__anext__())

            except StopAsyncIteration:
                break
    else:
        yield from generator


# from asgiref.sync import sync_to_async
# anyio.to_thread.run_sync


if __name__ == '__main__':
    from meutils.pipe import *


    async def async_generator():
        for i in range(10):
            await asyncio.sleep(1)
            yield i


    async_generator() | xprint
