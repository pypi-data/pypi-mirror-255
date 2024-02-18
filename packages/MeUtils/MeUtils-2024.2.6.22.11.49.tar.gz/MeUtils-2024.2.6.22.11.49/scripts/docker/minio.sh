#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2024/1/3 14:35
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :

docker run \
  -p 19000:9000 \
  -p 9090:9090 \
  --net=host \
  --name minio \
  -d --restart=always \
  -e "MINIO_ACCESS_KEY=chatllm" \
  -e "MINIO_SECRET_KEY=chatllmchatllm" \
  -v /www/data/minio/data:/data \
  -v /www/data/minio/config:/root/.minio \
  minio/minio server \
  /data --console-address ":9090" -address ":19000"
