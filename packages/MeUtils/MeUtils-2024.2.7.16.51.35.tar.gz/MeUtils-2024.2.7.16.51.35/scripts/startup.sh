#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/12/13 17:59
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  : 开机启动脚本
#python -m jupyter lab password
# python -m jupyter lab --generate-config
export PORT=39000
lsof -i:$PORT | grep "LISTEN" | awk '{print $2}' | xargs kill -9 && sleep 10

#nohup python -m jupyter lab --ip='*' --port=$PORT --notebook-dir='/www' --no-browser --allow-root >jupyter_start.log 2>&1 &

python -m jupyter lab --ip='*' --port=$PORT --notebook-dir='/www' --no-browser --allow-root >jupyter_start.log
