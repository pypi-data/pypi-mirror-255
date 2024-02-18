#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2024/2/1 13:55
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  : https://github.com/Unstructured-IO/unstructured-api#--

docker run -p 7777:8000 -d --rm --name unstructured-api --cpus 8 downloads.unstructured.io/unstructured-io/unstructured-api:latest
