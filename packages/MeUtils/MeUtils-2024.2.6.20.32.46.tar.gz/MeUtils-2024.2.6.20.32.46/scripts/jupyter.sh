#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/12/13 12:20
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :

export PORT=9955
lsof -i:$PORT | grep "LISTEN" | awk '{print $2}' | xargs kill -9

nohup python -m jupyter lab --ip='*' --port=$PORT --notebook-dir='/' --no-browser --allow-root >jupyter_start.log 2>&1 &


nohup python -m jupyter lab --ip='*' --port=9955 --no-browser --allow-root >jupyter_start.log 2>&1 &
