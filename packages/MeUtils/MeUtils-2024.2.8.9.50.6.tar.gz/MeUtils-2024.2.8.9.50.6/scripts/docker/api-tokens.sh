#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2024/1/17 16:44
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :
docker build -t chatllm/api-tokens:chatfire .
docker tag apitool chatllm/api-tokens:chatfire # 重命名
docker push chatllm/api-tokens:chatfire


docker run --name api-tokens -d -p 39777:80 chatllm/api-tokens:chatllm
docker run --name api-tokens -d -p 39777:80 chatllm/api-tokens:chatfire
docker run --name api-tokens -d -p 38899:80 chatllm/api-tokens:chatfire

