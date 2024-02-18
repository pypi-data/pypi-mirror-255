#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2024/1/5 13:26
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  : https://mp.weixin.qq.com/s/NZ9Y-aWhf0qRH4cokZcNsA

docker run -d --name kuma --restart=always -p 3001:3001 \
  -v /www/data/kuma:/app/data \
  -v /var/run/docker.sock:/var/run/docker.sock \
  louislam/uptime-kuma
