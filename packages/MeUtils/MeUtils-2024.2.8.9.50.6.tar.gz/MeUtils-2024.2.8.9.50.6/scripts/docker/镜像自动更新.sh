#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/12/15 08:41
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  : https://mp.weixin.qq.com/s/bRzoTwL5j641ZPSAKlAAEg

# 指定更新nginx和redis容器名称
docker run -d \
  --name watchtower \
  --restart unless-stopped \
  -e TZ=Asia/Shanghai \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e TZ=Asia/Shanghai \
  containrrr/watchtower -c

# 比如每天凌晨 2 点检查一次更新：
docker run -d \
  --name watchtower \
  --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower -c \
  --schedule "0 0 6 * * *"

# 手动更新
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower -c \
  --run-once \
  justsong/one-api calciumion/new-api:latest yidadaa/chatgpt-next-web lobehub/lobe-chat

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower -c \
  --run-once \
  calciumion/new-api:latest
