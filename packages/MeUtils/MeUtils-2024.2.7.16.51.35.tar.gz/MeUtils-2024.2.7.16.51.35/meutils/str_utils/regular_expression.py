#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : re_utils
# @Time         : 2022/5/12 下午2:03
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

zh = re.compile('[a-zA-Z\u4e00-\u9fa5]+')  # 中文 + 字母
nozh = re.compile('[^a-zA-Z\u4e00-\u9fa5]+')  # 中文 + 字母


# re.sub(r'=(.+)', r'=123','s=xxxxx')


def get_parse_and_index(text, pattern):
    """
    text = 'The quick brown cat jumps over the lazy dog'
    get_parse_and_index(text, r'cat')
    """
    # 编译正则表达式模式
    regex = re.compile(pattern)

    # 使用re.finditer匹配文本并返回匹配对象迭代器
    matches = regex.finditer(text)

    # 遍历匹配对象迭代器，输出匹配项及其在文本中的位置
    for match in matches:  # 大数据
        yield match.start(), match.end(), match.group()


@lru_cache
def parse_url(text: str):
    # url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+|#]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    # url_pattern = 'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    url = re.findall(url_pattern, str(text))

    return url


if __name__ == '__main__':
    text = """7个正规url
    这是一段包含URL的文本，https://www.google.com 是一个URL，另一个URL是http://www.baidu.com
    解读这个文本https://www.url1.com
    https://www.url2.com 解读这个文本
    http://www.url2.com 解读这个文本

    https://www.url2.com解读这个文本
    
    总结 waptianqi.2345.com/wea_history/58238.html
    
    总结 https://waptianqi.2345.com/wea_history/58238.htm
    """

    print(parse_url(text))

    print(parse_url("http://154.3.0.117:39666/docs#/default/get_content_preview_spider_playwright_get"))
