#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : feishu
# @Time         : 2021/1/20 6:04 下午
# @Author       : yuanjie
# @Email        : meutils@qq.com
# @Software     : PyCharm
# @Description  : todo: 输出json优化

from meutils.pipe import *


@background_task
def send_message(
        content: str = '',
        title: str = '',
        message: Optional[Dict] = None,
        url: Optional[str] = None,
        n: int = 1,
) -> str:
    if any((content, title)):

        contents = [content] if isinstance(content, str) else content  # todo: post_process

        message = message or {
            "msg_type": "interactive",
            "card": {
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": str(content),
                            "tag": "lark_md"
                        }
                    } for content in contents
                ],
                "header": {
                    "title": {
                        "content": str(title).title(),
                        "tag": "plain_text"
                    }
                }
            }
        }
        url = url or "https://open.feishu.cn/open-apis/bot/v2/hook/f7cf6f2a-30da-4e7a-ae6f-b48c8bb1ecf8"  # 测试群
        r = None
        for i in range(n):
            time.sleep(i ** 2)
            r = requests.post(url, json=message)
        return r and r.text


@decorator
def catch(
        fn: Callable,
        task_name: Optional[str] = None,
        trace: bool = True,
        url: Optional[str] = None,
        *args,
        **kwargs
):
    task_name = task_name or fn.__name__
    r = None
    try:
        # s = time.perf_counter()
        r = fn(*args, **kwargs)
        # content = f"Task done in {time.perf_counter() - s:.2f} s"

    except Exception as e:
        content = str(e)
        if trace:
            content = traceback.format_exc()
        send_message(title=task_name, content=content, url=url, n=3)

    return r


if __name__ == '__main__':
    # send_message(title="我是个标题", content=['我是一段内容\nabc'] * 3)

    # @catch(task_name='这是一个任务名')
    # def f():
    #     time.sleep(3)
    #     1 / 0
    #
    #
    # f()

    send_message("ERROR", title='GitHub Copilot Chat Error')
