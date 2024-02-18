#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/12/21 13:35
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  : 关联python 软连接

sudo rm /usr/bin/python && ln -s /www/server/pyporject_evn/versions/3.10.0/bin/python3 /usr/bin/python
sudo rm /usr/bin/pip && ln -s /www/server/pyporject_evn/versions/3.10.0/bin/pip3 /usr/bin/pip